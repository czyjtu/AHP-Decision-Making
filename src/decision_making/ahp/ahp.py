import numpy as np
from ..base.mcda import MCDA, A
from ..base.criterium import Criterium
from ..base.preference import Preference
from typing import Dict, List, Set, Tuple


class ComprehensionMatrix:
    RI = [1e-5, 1e-5, 1e-5, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]

    def __init__(self, Matrix: np.matrix):
        self.matrix: np.matrix = Matrix
        self.weights = np.array(0)

    def complete(self) -> None:
        for i in range(len(self.matrix)):
            self.matrix[i, i] = 1.0

        for i in range(len(self.matrix)):
            for j in range(len(self.matrix)):
                if self.matrix[i, j] != 0:
                    self.matrix[j, i] = 1 / self.matrix[i, j]

    def __contain_zeros(self):
        return .0 in self.matrix.reshape(-1) or 0 in self.matrix.reshape(-1)

    def __zero_indexes(self):
        return [(i, j) for i in range(len(self.matrix)) for j in range(len(self.matrix)) if self.matrix[i, j] == 0]

    def __comprehended_index(self, x, y):
        """
        method finding index i that (x, i) and (i, y)
        :param x:
        :param y:
        :return:
        """
        xs, ys = np.array(self.matrix)[x], np.array(self.matrix[:, y].reshape(-1))[0]
        a = no_zero_index(xs).intersection(no_zero_index(ys))
        if len(a) > 0:
            return a.pop()
        else:
            return None

    def complete_comprehensions(self):
        self.complete()
        t: bool = False
        to_complite = self.__zero_indexes()
        while self.__contain_zeros():
            if t:
                missing = self.__missing_comperes()
                raise ValueError(
                    "incomplete matrix!\n"
                    f"missing comprehensions: \n" +
                    repr({"one of: " + str(i) for i in missing})
                                 )
            t = True
            i = 0
            while i < len(to_complite):
                x, y = to_complite[i]
                a = self.__comprehended_index(x, y)
                if a is not None:
                    self.matrix[x, y] = self.matrix[x, a] * self.matrix[a, y]
                    self.matrix[y, x] = 1 / self.matrix[x, y]
                    del to_complite[i]
                    to_complite.remove((x, y))
                    t = False
                else:
                    i += 1

    def __sub_graphs(self):
        missing = []
        indexes = {i for i in range(len(self.matrix))}
        while len(indexes) > 0:
            i = indexes.pop()
            a = no_zero_index(np.array(self.matrix)[i])
            missing.append(list(a))
            indexes = indexes.difference(a)
        return missing

    def __missing_comperes(self):
        sub_graphs = self.__sub_graphs()
        print(sub_graphs)
        missing = []
        for i in range(len(sub_graphs) - 1):
            missing.append({(x, y) for x in sub_graphs[i] for y in sum(sub_graphs[i+1:], [])})
        return missing


    def calculate_weights(self):
        matrix = np.array(self.matrix)
        suma = sum(matrix.reshape(-1))
        self.weights = sum(matrix) / suma

    def CI(self) -> float:
        self.complete()
        # print(self.matrix)
        self.calculate_weights()
        sum_vec = sum(np.array(self.matrix.transpose()))
        lambda_max = sum_vec @ self.weights
        n = len(self.matrix)
        ci = (lambda_max - n) / (n - 1)
        return ci

    def CR(self) -> float:
        # Consistency ratio, defined by Saaty
        CR = self.CI() / self.RI[len(self.matrix)]
        return CR

    def __repr__(self):
        return repr(self.matrix)


def compere(l: List[Dict], criteria_id) -> List[List]:
    result=[]
    if type(l[0][criteria_id]) == bool:
        for i in range(len(l) - 1):
            for j in range(i + 1, len(l)):
                result.append([l[i]['id'], l[j]['id'], comp_bool(l[j][criteria_id], l[i][criteria_id])])
    else:
        for i in range(len(l) - 1):
            for j in range(i+1, len(l)):
                result.append([l[i]['id'], l[j]['id'], l[j][criteria_id] / l[i][criteria_id]])

    return result

def comp_bool(x, y):
    if (not x and not y) or (x and y):
        return 1
    elif x:
        return 2
    else:
        return 1/2

class AHP(MCDA):
    def __init__(self, criteria: List[Criterium], comprehension_list: List[List], alternative_list: List[Dict]):
        self.criteria_dict: Dict[Criterium] = {cr.id: cr for cr in criteria}

        sorted_comprehensions: Dict[List[List]] = {p.id: [] for p in criteria if not p.is_leaf}
        for com in comprehension_list:
            sorted_comprehensions[self.criteria_dict[com[0]].parent_criterium].append(com)
        self.matrices = {ids: ComprehensionMatrix(choice_list2matrix(x)) for ids, x in sorted_comprehensions.items()}

        #TODO CRs to com_matrix attribute
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

    def __get_single_alternative_value(self, alternative: Dict, criterium: Criterium) -> float:
        if not criterium.is_leaf:
            return np.array(
                map(lambda x: self.get_alternative_value(alternative, self.criteria_dict[x]), criterium.sub_criteria)) @ \
                   self.matrices[criterium.id].weights
        else:
            return alternative[criterium.id]

    def get_alternative_value(self, alternative:A, criterium:Criterium) -> float:
        """
        Method getting value of single alternative in comprehension matrix of given criteria
        :param alternative:
        :param criterium:
        :return:
        """
        x = self.alternative_comprehension[criterium.id].weights[self.alternative_labels.index(alternative['id'])]
        # print(x)
        if criterium.higher_better:
            return x
        else:
            return 1 - x


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

def mix(s1, s2)-> Set[Set]:
    return {{i, j} for i in s1 for j in s2}


def random_matrix(n, q):
    m = np.random.random((n, n)) * q + 1
    m = np.matrix(list(map(lambda x: list(map(lambda x1: float(int(x1)), x)), m)))
    return m

def calc_RI(n, q, mt=25):
    CIs = [ComprehensionMatrix(random_matrix(n, q)).CI() for _ in range(mt)]
    return np.mean(CIs)



if __name__ == '__main__':
    print(calc_RI(5, 9))



