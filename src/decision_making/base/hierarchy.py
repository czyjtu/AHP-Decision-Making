from src.decision_making.base import Criterium
from typing import Sequence, TypeVar, Tuple
from src.decision_making.base.mcda import MCDA, A



class Hierarchy:
    def __init__(self, root_criterium: Criterium):
        self.root_criterium = root_criterium
        self.criteria = dict()
        self.root_criterium.apply(lambda c: self.criteria.update({c.id: c}))


    def rank_alternatives(self, alternatives:Sequence[A],  model:MCDA) -> Sequence[Tuple[A, float]]:
        ranked = list(map(lambda a: (a, self.rank_wrt_criterium(a, self.root_criterium, model)), alternatives))
        return sorted(ranked, key=lambda item: -item[1])


    def rank_wrt_criterium(self, alternative:A, criterium:Criterium, model:MCDA) -> float:
        if criterium.is_leaf:
            return model.get_alternative_value(alternative, criterium) * model.priority_of(criterium)
        score = 0 
        for sub in criterium.sub_criteria:
            sub_score = self.rank_wrt_criterium(alternative, sub, model)
            score += model.priority_of(criterium) * sub_score 
        return score * model.priority_of(criterium)





    