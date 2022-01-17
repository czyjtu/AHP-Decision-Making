from enum import Enum
import numpy as np
from abc import ABC, abstractmethod


class RankingMethod(ABC):
    @abstractmethod
    def calculate(self, m: np.ndarray) -> np.ndarray:
        pass


class EVMRanking(RankingMethod):
    def calculate(self, m: np.ndarray) -> np.ndarray:
        eig_val, eig_vec = map(np.real, np.linalg.eig(m))
        max_index = np.argmax(eig_val)
        weights = eig_vec[:, max_index]
        return weights / np.sum(weights)


class GMMRanking(RankingMethod):
    def calculate(self, m: np.ndarray) -> np.ndarray:
        means = np.exp(np.log(m).mean(axis=1))
        means /= sum(means)
        return means
