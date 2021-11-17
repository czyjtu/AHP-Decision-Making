from src.decision_making.base import Criterium
from typing import Sequence, TypeVar, Tuple
from src.decision_making.base.mcda import MCDA, A



class Hierarchy:
    def __init__(self, criteria:Sequence[Criterium]):
        self.criteria = {cr.id: cr for cr in criteria} 
        self.root_criteria = next(filter(lambda c: c.is_root, criteria))


    def rank_alternatives(self, alternatives:Sequence[A],  model:MCDA) -> Sequence[Tuple[A, float]]:
        print(alternatives)
        ranked = list(map(lambda a: (a, self.rank_wrt_criterium(a, self.root_criteria, model)), alternatives))
        return sorted(ranked, key=lambda item: -item[1])


    def rank_wrt_criterium(self, alternative:A, criterium:Criterium, model:MCDA) -> float:
        if criterium.is_leaf:
            return model.get_alternative_value(alternative, criterium) * model.priority_of(criterium)
        score = 0 
        for sub_id in criterium.sub_criteria:
            sub_score = self.rank_wrt_criterium(alternative, self.criteria[sub_id], model)
            
            score += model.priority_of(criterium) * sub_score 
        return score * model.priority_of(criterium)





    