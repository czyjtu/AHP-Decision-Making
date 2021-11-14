from src.decision_making.base import Criterium
from typing import Sequence
from abc import ABC, abstractmethod 


class MCDA(ABC):
    @abstractmethod 
    def rank_of(self, c:Criterium):
        pass 