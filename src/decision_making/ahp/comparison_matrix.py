from math import log10
from .ranking_method import RankingMethod, EVMRanking, GMMRanking
from .utils import no_zero_index
from itertools import chain
import numpy as np
from typing import List, Tuple, Set, Dict

class MissingComparisonsError(ValueError):
    def __init__(self, message='incorrect number of comparisons ', missing_comparisons=None, missing_comparisons_names=None):
        super().__init__(message)
        self.missing_comparisons = missing_comparisons
        self.missing_comparisons_names = missing_comparisons_names


class ComparisonMatrix:
    RI = [0, 0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
    ranking_methods = {
        "EVM": EVMRanking,
        "GMM": GMMRanking
        }

    def __init__(self, comparison_list: List[Tuple[str, str, float]], ranking_method: RankingMethod, required_size=None):
        self.index_of = self._build_mapping(comparison_list)
        self.matrix = self._build_matrix(comparison_list, required_size=required_size)
        if self.__contain_zeros():
            self.complete_comparisons()
        self.weights = self._calculate_weights(ranking_method)
        self.cr = self.CR()
        try:
            self.gi = self.GI()
        except AssertionError:
            self.gi = None
        # self.inconsistency_index = self.calculate_inconsistency()

    def __getitem__(self, key):
        return self.weights.get(key, None)

    def _build_matrix(self, comp_list: List[Tuple[str, str, float]], required_size=None):
        """
        build matrix defined by given comparisons
        :param comp_list:
        :param required_size: optional required size
        (matrix will then have exacly this size,
        notice that if you give smaller size then amount of items between there are comparisons with,
        it will throw a ValueError)
        :return: created matrix
        """
        if required_size != None:
            n = required_size
            if n < len(self.index_of):
                raise ValueError("too small :param required_size:")
        else:
            n = len(self.index_of)
        M = np.zeros((n, n))
        for i in range(n):
            M[i][i] = 1.
        for a, b, pref in comp_list:
            M[self.index_of[a]][self.index_of[b]] = pref
            M[self.index_of[b]][self.index_of[a]] = 1 / pref
        return M

    @staticmethod
    def _build_mapping(comp_list: List[Tuple[str, str, float]]):
        ids = set(chain.from_iterable([comp[:2] for comp in comp_list]))
        return {id_: idx for idx, id_ in enumerate(ids)}

    def _calculate_weights(self, ranking_method: RankingMethod) -> Dict:
        """
        calculates weights using :param ranking_method:
        :return: Dict[weights]
        """
        weights = ranking_method.calculate(self.matrix)
        return {id_: weights[idx] for id_, idx in self.index_of.items()}

    def __common_comparison_index(self, x, y) -> Set:
        """
        method finding index i that positions on (x, i) and (i, y) are not zero
        :param x: index of first item
        :param y: index of second item
        :return: indexes of items that both x and y items have comparison with
        """
        xs, ys = np.array(self.matrix)[x], np.array(self.matrix[:, y].reshape(-1))
        a = no_zero_index(xs).intersection(no_zero_index(ys))
        return a

    @staticmethod
    def __name_on_index(indexes, i):
        name = list(filter(lambda x: x[1] == i, indexes.items()))
        return str(name[0][0] if len(name) > 0 else f'unknown{i}')

    def __contain_zeros(self):
        return .0 in self.matrix.reshape(-1) or 0 in self.matrix.reshape(-1)

    def __zero_indexes(self):
        return [(i, j) for i in range(len(self.matrix)) for j in range(len(self.matrix)) if self.matrix[i, j] == 0]

    def complete_comparisons(self):
        """
        this method tries to complete matrix
        filling it with comparisons obtained from mean of other comparisons
        if matrix is full does nothing,
        if completing is impossible throws an MissingComparisonsError, containing missing values
        :return: None
        """
        t: bool = False
        to_complite = self.__zero_indexes()
        while self.__contain_zeros():
            if t:
                missing = self.__missing_comperes()
                missing_names = list(map(lambda y: set(map(lambda x:
                                                           (
                    self.__name_on_index(self.index_of, x[0]),
                    self.__name_on_index(self.index_of, x[1])
                                                           ),
                                                           y)), missing))
                raise MissingComparisonsError(
                    "incomplete matrix!\n"
                    f"missing comparisons: \n" +
                    repr({"one of: " + str(i) for i in missing_names}),
                    missing_comparisons=missing,
                    missing_comparisons_names=missing_names
                )
            t = True
            i = 0
            while i < len(to_complite):
                x, y = to_complite[i]
                a = self.__common_comparison_index(x, y)
                if len(a) > 0:
                    self.matrix[x, y] = np.mean([self.matrix[x, j] * self.matrix[j, y] for j in a])
                    self.matrix[y, x] = 1 / self.matrix[x, y]
                    del to_complite[i]
                    to_complite.remove((y, x))
                    t = False
                else:
                    i += 1

    def __sub_graphs(self):
        """
        method used to finding  lists of indexes of items between which there is a comparison
        :return: List[List[index]]
        """
        sub_graphs = []
        indexes = {i for i in range(len(self.matrix))}
        while len(indexes) > 0:
            i = indexes.pop()
            a = no_zero_index(np.array(self.matrix)[i])
            sub_graphs.append(list(a))
            indexes = indexes.difference(a)
        return sub_graphs

    def __missing_comparisons(self):
        """
        method finding missing comparisons
        :return: List[Set[Tuple_of_missing_comparison]]
        """
        sub_graphs = self.__sub_graphs()
        # print(sub_graphs)
        missing = []
        for i in range(len(sub_graphs) - 1):
            missing.append({(x, y) for x in sub_graphs[i] for y in sum(sub_graphs[i + 1:], [])})
        return missing

    def CI(self) -> float:
        """
        :return: Consistency Index
        """
        sum_vec = sum(np.array(self.matrix.transpose()))
        w = np.array(list(self.weights.values()))
        lambda_max = sum_vec @ w
        n = len(self.matrix)
        ci = (lambda_max - n) / (n - 1)
        return ci

    def GI(self):
        """
        :return: Geometric Consistency Index
        """
        n = len(self.matrix)
        assert n > 2, "matrix size cannot be less than 2"
        assert not self.__contain_zeros(), "matrix still contains zeros"
        w = np.array(list(self.weights.values()))
        total_log_error = 0
        for i in range(n - 1):
            for j in range(i + 1, n):
                total_log_error += log10(self.matrix[i, j] * w[j] / w[i]) ** 2

        return total_log_error * (2 / ((n - 1) * (n - 2)))

    def CR(self) -> float:
        """
        :return: Consistency ratio, defined by Saaty
        """
        CR = self.CI() / self.RI[len(self.matrix)]
        return CR

    def __repr__(self):
        return repr(self.matrix)
