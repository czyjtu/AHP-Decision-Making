from enum import Enum, auto
import numpy as np
from src.decision_making.ahp.utils import gmean

class RankingMethod(Enum):
    EVM = "EVM"
    GMM = "GMM"


def evm_weights(m: np.ndarray) -> np.ndarray:
    eig_val, eig_vec = map(np.real, np.linalg.eig(m))
    max_index = np.argmax(eig_val)
    weights = eig_vec[:, max_index]
    return weights / np.sum(weights)


def gmm_weights(m: np.ndarray) -> np.ndarray:
    means = np.exp(np.log(m).mean(axis=1))
    means /= sum(means)
    return means
