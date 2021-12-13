import numpy as np 
from typing import List, Dict

def evm_weights(m: np.ndarray) -> np.ndarray:
    eig_val, eig_vec = map(np.real, np.linalg.eig(m))
    max_index = np.argmax(eig_val)
    weights = eig_vec[:, max_index]
    return weights / np.sum(weights)


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

def no_zero_index(l) -> set:
    return {i for i in range(len(l)) if l[i] != 0}