from decision_making.hierarchy.criterium import Criterium
from typing import TypeVar
from abc import ABC, abstractmethod


A = TypeVar("A")  # alternative type


class MCDA(ABC):
    """
    Abstract class defining interface for any Multiple-criteria decision analysis method
    """

    @abstractmethod
    def get_alternative_value(self, alternative: A, criterium: Criterium) -> float:
        """
        Method calculate value of the given alternative with respect to the Criterium
        """
        pass

    @abstractmethod
    def priority_of(self, c: Criterium) -> float:
        """
        Method calculates priority of the given Criterium
        :param c: Criterium
        :return priority: return float in range[0, 1] representing priority of the given criterium
        """
        pass
