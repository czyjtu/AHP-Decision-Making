from src.decision_making.base import Criterium
from typing import Sequence, TypeVar, Tuple

from src.decision_making.base.mcda import MCDA

A = TypeVar('A') # alternative type 

class Hierarchy:
    def __init__(self, criteria:Sequence[Criterium]):
        self.criteria = {cr.id: cr for cr in criteria} 
        self.leaves = {cr for cr in criteria if cr.is_leaf}
        self.root_criteria = next(lambda c: c.is_root, criteria)


    def rank_alternatives(self, alternatives:Sequence[A],  model:MCDA) -> Sequence[Tuple[A, float]]:
        return list(map(lambda a: (a, self._rank(a, self.root_criteria, model)), alternatives))


    def rank_wrt_criterium(self, alternative:A, criterium:Criterium, model:MCDA) -> float:
        if criterium.is_leaf:
            return alternative[Criterium.id] * model.weight_of(criterium)
        score = 0 
        for sub_id in alternative.sub_criteria:
            sub_score = self.rank_wrt_criterium(alternative, self.criteria[sub_id], model)
            score += model.weight_of(criterium) * sub_score 
        return score * model.weight_of(criterium)





    