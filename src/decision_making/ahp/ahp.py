import numpy as np
from ..base.mcda import MCDA, A
from ..base.criterium import Criterium
from ..base.preference import Preference
from typing import Dict, List


class ComprehensionMatrix:
    RI = [0, 0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]

    def __init__(self, Matrix: np.matrix):
        self.matrix: np.matrix = Matrix
        self.weights = np.array(0)

    def complete(self) -> None:
        for i in range(len(self.matrix)):
            self.matrix[i, i] = 1.0

        for i in range(len(self.matrix)):
            for j in range(i, len(self.matrix)):
                if self.matrix[i, j] != .0:
                    self.matrix[j, i] = 1 / self.matrix[i, j]

    def __contain_zeros(self):
        return .0 in self.matrix.reshape(-1)

    def __comprehended_index(self, x, y):
        a = no_zero_index(self.matrix[x]).intersection(no_zero_index(self.matrix[y]))
        if a is not None:
            return list(a)[0]
        else:
            return None

    def complete_comprehensions(self):
        self.complete()
        t: bool = False
        while self.__contain_zeros():
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

    def __repr__(self):
        return repr(self.matrix)


def compere(l: List[Dict], criteria_id) -> List[List]:
    result=[]
    for i in range(len(l) - 1):
        for j in range(i+1, len(l)):
            result.append([l[i]['id'], l[j]['id'], l[i][criteria_id] / l[j][criteria_id]])

    return result


class AHP(MCDA):
    def __init__(self, criteria: List[Criterium], comprehension_list: List[List], alternative_list: List[Dict]):
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

        self.alternative_dict: Dict[Dict] = {a['id']: a for a in alternative_list}
        self.alternative_labels = sorted(list(map(lambda x: x['id'], alternative_list)))
        self.alternative_comprehension = dict()
        for cr_id in [cr.id for cr in criteria if cr.is_leaf]:
            self.alternative_comprehension[cr_id] = ComprehensionMatrix(comp_list2matrix(compere(alternative_list, cr_id)))
            self.alternative_comprehension[cr_id].CR()

    def priority_of(self, c: Criterium) -> float:
        return self.weights[c.id] if not c.is_root else 1


    def get_alternative_value(self, alternative:A, criterium:Criterium) -> float:
        return self.alternative_comprehension[criterium.id].weights[self.alternative_labels.index(alternative['id'])]


def choice_list2matrix(choices: List[List]) -> np.matrix:
    n = num_of_points(len(choices))
    if n == 0: raise ValueError("Incorrect number of comprehensions!")
    labels = sorted(list(set(sum([[x[0], x[1]] for x in choices], []))))
    result_matrix: np.matrix = np.matrix(np.zeros((n, n)))

    for comprehension in choices:
        i, j = labels.index(comprehension[0]), labels.index(comprehension[1])
        result_matrix[i, j] = comprehension[2].value

    return result_matrix

def comp_list2matrix(choices: List[List]) -> np.matrix:
    n = num_of_points(len(choices))
    if n == 0: raise ValueError("Incorrect number of comprehensions!")
    labels = sorted(list(set(sum([[x[0], x[1]] for x in choices], []))))
    result_matrix: np.matrix = np.matrix(np.zeros((n, n)))

    for comprehension in choices:
        i, j = labels.index(comprehension[0]), labels.index(comprehension[1])
        result_matrix[i, j] = comprehension[2]

    return result_matrix

def num_of_points(N: int) -> int:
    n = 1
    while n <= N + 1:
        if n * (n - 1) / 2 == N:
            return n
        n += 1
    return 0


def no_zero_index(l) -> set:
    return {i for i in range(len(l)) if l[i] != 0}


