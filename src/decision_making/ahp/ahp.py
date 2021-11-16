import numpy as np
from ..base.mcda import MCDA, A
from ..base.criterium import Criterium
from typing import Dict, List


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
                        self.matrix[i, j] = 1 / self.matrix[j, i]
                    elif self.matrix[j, i] == .0:
                        self.matrix[j, i] = 1 / self.matrix[i, j]
        except ZeroDivisionError:
            raise ValueError("incomplete matrix!")

    def calculate_weights(self):
        matrix = np.array(self.matrix)
        suma = sum(matrix.reshape(-1))
        self.weights = sum(matrix) / suma

    def CR(self) -> float:
        self.complete()
        self.calculate_weights()
        sum_vec = sum(np.array(self.matrix.transpose()))
        lambda_max = sum_vec @ self.weights
        n = len(self.matrix)
        CI = (lambda_max - n) / (n - 1)
        CR = CI / self.RI[n]
        return CR


class AHP(MCDA):
    def __init__(self, criteria: List[Criterium], comprehension_list: List[List]):
        self.criteria_dict: Dict[Criterium] = {cr.id: cr for cr in criteria}

        sorted_comprehensions: Dict[List[List]] = {p.id: [] for p in criteria if not p.is_leaf}
        for com in comprehension_list:
            sorted_comprehensions[self.criteria_dict[com[0]].parent_criterium].append(com)
        self.matrices = {ids: ComprehensionMatrix(choice_list2matrix(x)) for ids, x in sorted_comprehensions.items()}

        self.CRs = {ids: matrix.CR() for ids, matrix in self.matrices.items()}

        self.weights = {}
        for ids in sorted_comprehensions.keys():
            sub_criteria_list = list(sorted(self.criteria_dict[ids].sub_criteria))
            for i in range(len(sub_criteria_list)):
                self.weights[sub_criteria_list[i]] = self.matrices[ids].weights[i]

    def priority_of(self, c: Criterium) -> float:
        return self.weights[c.id]

    def get_alternative_value(self, alternative: Dict, criterium: Criterium) -> float:
        if not criterium.is_leaf:
            return np.array(
                map(lambda x: self.get_alternative_value(alternative, self.criteria_dict[x]), criterium.sub_criteria)) @\
                   self.matrices[criterium.id].weights
        else:
            return alternative[criterium.id]


def choice_list2matrix(choices: List[List]) -> np.matrix:
    n = num_of_points(len(choices))
    if n == 0: raise ValueError("Incorrect number of comprehensions!")
    labels = sorted(list(set(sum([[x[0], x[1]] for x in choices], []))))
    result_matrix: np.matrix = np.matrix(np.zeros((n, n)))

    for comprehension in choices:
        i, j = labels.index(comprehension[0]), labels.index(comprehension[1])
        result_matrix[i, j] = comprehension[2].value

    return result_matrix


def num_of_points(N: int) -> int:
    n = 1
    while n <= N:
        if n * (n - 1) / 2 == N:
            return n
        n += 1
    return 0
