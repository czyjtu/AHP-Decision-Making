import numpy as np
from ..base.mcda import MCDA
from ..base.criterium import Criterium
from typing import is_typeddict, Dict


class ComprehensionMatrix:
    RI = [0, 0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]

    def __init__(self, Matrix: np.matrix):
        self.matrix: np.matrix = Matrix
        self.weights = np.array(0)

    def complete(self) -> None:
        for i in range(len(self.matrix)):
            self.matrix[i, i] = 1.0

        try:
            for i in range(len(self.matrix)):
                for j in range(len(self.matrix)):
                    if self.matrix[i, j] == .0:
                        self.matrix[i, j] = 1/self.matrix[j, i]
                    elif self.matrix[j, i] == .0:
                        self.matrix[j, i] = 1 / self.matrix[i, j]
        except ZeroDivisionError:
            raise ValueError("incomplete matrix!")

    def calculate_weights(self):
        matrix = np.array(self.matrix)
        sum = sum(matrix.reshape(-1))
        self.weights = sum(matrix) / sum

    def CR(self) -> float:
        self.complete()
        self.calculate_weights()
        sum_vec = sum(np.array(self.matrix.transpose()))
        lambda_max = sum_vec @ self.weights
        n = len(self.matrix)
        CI = (lambda_max - n) / (n-1)
        CR = CI / self.RI[n]
        return CR


class AHP(MCDA):
    def __init__(self, hierarchy_tree: Dict[Criterium], comprehension_matrices: Dict[np.matrix]):
        self.matrices = {ids: ComprehensionMatrix(x) for ids, x in comprehension_matrices.items()}
        self.CRs = {ids: matrix.CR() for ids, matrix in self.matrices.items()}
        self.weights = {}
        for ids in comprehension_matrices.keys():
            sub_criteria_list = list(sorted(map(lambda x: x[0], hierarchy_tree[ids].sub_criteria)))
            for i in range(len(sub_criteria_list)):
                self.weights[sub_criteria_list[i]] = comprehension_matrices[ids].weights[i]

    def priority_of(self, c:Criterium) -> float:
        return self.weights[c.id[0]]









