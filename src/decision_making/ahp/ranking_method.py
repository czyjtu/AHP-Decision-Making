from enum import Enum, auto
import numpy as np

class RankingMethod(Enum):
    EVM = auto()
    GMM = auto()


def evm_weights(m: np.ndarray) -> np.ndarray:
    eig_val, eig_vec = map(np.real, np.linalg.eig(m))
    max_index = np.argmax(eig_val)
    weights = eig_vec[:, max_index]
    return weights / np.sum(weights)