import math

import numpy as np
from src.decision_making.ahp.ranking_method import RankingMethod
from src.decision_making.ahp.utils import choice_list2matrix, comp_list2matrix
from src.decision_making.ahp.comparison_matrix import ComprehensionMatrix
from src.decision_making.base import MCDA, A, Preference, Criterium
from typing import Dict, List, Mapping
from ..base.mcda import MCDA, A
from ..base.criterium import Criterium
from ..base.preference import Preference
from typing import Dict, List, Set, Tuple


# class ComprehensionMatrix:
#     RI = [1e-5, 1e-5, 1e-5, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
#
#     def __init__(self, Matrix: np.matrix):
#         self.matrix: np.matrix = Matrix
#         self.complete()
#         if self.__contain_zeros():
#             self.complete_comprehensions()
#         self.weights = self.calculate_weights()
#         self.cr = self.CR()
#         self.gi = self.GI()
#
#     def complete(self) -> None:
#         for i in range(len(self.matrix)):
#             self.matrix[i, i] = 1.0
#
#         for i in range(len(self.matrix)):
#             for j in range(len(self.matrix)):
#                 if self.matrix[i, j] != 0:
#                     self.matrix[j, i] = 1 / self.matrix[i, j]
#
#     def __contain_zeros(self):
#         return .0 in self.matrix.reshape(-1) or 0 in self.matrix.reshape(-1)
#
#     def __zero_indexes(self):
#         return [(i, j) for i in range(len(self.matrix)) for j in range(len(self.matrix)) if self.matrix[i, j] == 0]
#
#     def __comprehended_index(self, x, y):
#         """
#         method finding index i that (x, i) and (i, y)
#         :param x:
#         :param y:
#         :return:
#         """
#         xs, ys = np.array(self.matrix)[x], np.array(self.matrix[:, y].reshape(-1))[0]
#         a = no_zero_index(xs).intersection(no_zero_index(ys))
#         if len(a) > 0:
#             return a.pop()
#         else:
#             return None
#
#     def complete_comprehensions(self):
#         t: bool = False
#         to_complite = self.__zero_indexes()
#         while self.__contain_zeros():
#             if t:
#                 missing = self.__missing_comperes()
#                 raise ValueError(
#                     "incomplete matrix!\n"
#                     f"missing comprehensions: \n" +
#                     repr({"one of: " + str(i) for i in missing})
#                 )
#             t = True
#             i = 0
#             while i < len(to_complite):
#                 x, y = to_complite[i]
#                 a = self.__comprehended_index(x, y)
#                 if a is not None:
#                     self.matrix[x, y] = self.matrix[x, a] * self.matrix[a, y]
#                     self.matrix[y, x] = 1 / self.matrix[x, y]
#                     del to_complite[i]
#                     to_complite.remove((x, y))
#                     t = False
#                 else:
#                     i += 1
#
#     def __sub_graphs(self):
#         missing = []
#         indexes = {i for i in range(len(self.matrix))}
#         while len(indexes) > 0:
#             i = indexes.pop()
#             a = no_zero_index(np.array(self.matrix)[i])
#             missing.append(list(a))
#             indexes = indexes.difference(a)
#         return missing
#
#     def __missing_comperes(self):
#         sub_graphs = self.__sub_graphs()
#         print(sub_graphs)
#         missing = []
#         for i in range(len(sub_graphs) - 1):
#             missing.append({(x, y) for x in sub_graphs[i] for y in sum(sub_graphs[i + 1:], [])})
#         return missing
#
#     def calculate_weights(self):
#         matrix = np.array(self.matrix)
#         suma = sum(matrix.reshape(-1))
#         return sum(matrix) / suma
#
#     def CI(self) -> float:
#         sum_vec = sum(np.array(self.matrix.transpose()))
#         lambda_max = sum_vec @ self.weights
#         n = len(self.matrix)
#         ci = (lambda_max - n) / (n - 1)
#         return ci
#
#     def GI(self):
#         """
#         Geometric Consistency Index
#         :return:
#         """
#         n = len(self.matrix)
#         total_log_error = 0
#         for i in range(n - 1):
#             for j in range(i + 1, n):
#                 total_log_error += math.log10(self.matrix[i, j] * self.weights[j] / self.weights[i]) ** 2
#
#         return total_log_error * (2 / ((n - 1) * (n - 2)))
#
#     def CR(self) -> float:
#         # Consistency ratio, defined by Saaty
#         CR = self.CI() / self.RI[len(self.matrix)]
#         return CR


class AHP(MCDA):
    def __init__(self, root_criterium: List[Criterium], criteria_comp: List[List], alter_comp: Mapping[str, List[List]], ranking_method: RankingMethod=RankingMethod.EVM):
        self.ranking_method = ranking_method
        self.root_criterium = root_criterium
        self.n = len(ComprehensionMatrix._build_mapping(list(alter_comp.values())[0]))
        self.criteria_dict = dict()
        self.root_criterium.apply(lambda c: self.criteria_dict.update({c.id: c}))
        self.criteria_matrices = self._criteria_matrices(criteria_comp)
        self.alternatives_matrices = self._alternative_matrices(alter_comp)


    def _criteria_matrices(self, criteria_comp: List[List]) -> Mapping[str, ComprehensionMatrix]:
        sorted_comprehensions: Dict[List[List]] = {p.id: [] for p in self.criteria_dict.values() if not p.is_leaf}
        for com in criteria_comp:
            sorted_comprehensions[self.criteria_dict[com[0]].parent_criterium].append(com)
        return {parent_id: ComprehensionMatrix(comparisons, self.ranking_method) for parent_id, comparisons in sorted_comprehensions.items()}


    def _alternative_matrices(self, alter_comp: Mapping[str, List[List]]) -> Mapping[str, ComprehensionMatrix]:
        return {criteria_id:
                    ComprehensionMatrix(comparisons, self.ranking_method, self.n)
        if isinstance(comparisons, List) else
                    self._alternative_matrices(comparisons)
                for criteria_id, comparisons in alter_comp.items()}


    def priority_of(self, c: Criterium) -> float:
        return 1 if c.parent_criterium is None else self.criteria_matrices[c.parent_criterium][c.id]


    def get_alternative_value(self, alternative:A, criterium:Criterium) -> float:
        cr = self.alternatives_matrices[criterium.id]
        if isinstance(cr, ComprehensionMatrix):
            return cr[alternative['id']]
        else:
            # print(alternative['id'])
            return float(np.mean([cm[alternative['id']] for cm in cr.values()]))

