from src.decision_making.base import Preference
from src.decision_making.ahp.utils import no_zero_index
from itertools import chain
import numpy as np
from typing import List, Tuple


class ComprehensionMatrix:
    RI = [0, 0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]

    def __init__(self, comparison_list: List[Tuple[str, str, Preference]]):
        self.index_of = self._build_mapping(comparison_list)
        self.matrix = self._build_matrix(comparison_list)
        self.weights = self._calculate_weights()
        # self.inconsistency_index = self.calculate_inconsistency()
    

    def __getitem__(self, key):
        return self.weights.get(key, None)

    
    def _build_matrix(self, comp_list: List[Tuple[str, str, Preference]]):
        n = len(self.index_of)
        M = np.zeros((n, n))
        for a, b, pref in comp_list:
            M[self.index_of[a]][self.index_of[b]] = pref
            M[self.index_of[b]][self.index_of[a]] = 1 / pref
        return M


    @staticmethod
    def _build_mapping(comp_list: List[Tuple[str, str, Preference]]):
        ids = set(chain.from_iterable([comp[:2] for comp in comp_list]))
        return {id_: idx for idx, id_ in enumerate(ids)}

    
    def _calculate_weights(self):
        matrix = np.array(self.matrix)
        suma = sum(matrix.reshape(-1))
        weights = sum(matrix) / suma
        return {id_: weights[idx] for id_, idx in self.index_of.items()}


    def complete(self) -> None:
        for i in range(len(self.matrix)):
            self.matrix[i, i] = 1.0

        for i in range(len(self.matrix)):
            for j in range(i, len(self.matrix)):
                if self.matrix[i, j] != .0:
                    self.matrix[j, i] = 1 / self.matrix[i, j]


    def __comprehended_index(self, x, y):
        a = no_zero_index(self.matrix[x]).intersection(no_zero_index(self.matrix[y]))
        if a is not None:
            return list(a)[0]
        else:
            return None


    def complete_comprehensions(self):
        self.complete()
        t: bool = False
        while .0 in self.matrix.reshape(-1):
            if t: raise ValueError("incomplete matrix!")
            t = True
            for i in range(len(self.matrix)):
                for j in range(len(self.matrix)):
                    if self.matrix[i, j] == 0:
                        a = self.__comprehended_index(i, j)
                        if a is not None:
                            self.matrix[i, j] = self.matrix[i, a] * self.matrix[a, j]
                            self.matrix[j, i] = 1 / self.matrix[i, j]
                            t = False


    def calculate_inconsistency(self) -> float:
        self.complete()
        self.calculate_weights()
        sum_vec = sum(np.array(self.matrix.transpose()))
        lambda_max = sum_vec @ self.weights
        n = len(self.matrix)
        CI = (lambda_max - n) / (n - 1)
        CR = CI / self.RI[n]
        return CR


    def __repr__(self):
        return repr(self.matrix)


