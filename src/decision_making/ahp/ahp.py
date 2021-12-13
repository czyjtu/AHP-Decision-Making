import numpy as np
from src.decision_making.ahp.ranking_method import RankingMethod
from src.decision_making.ahp.utils import choice_list2matrix, comp_list2matrix
from src.decision_making.ahp.comparison_matrix import ComprehensionMatrix
from src.decision_making.base import MCDA, A, Preference, Criterium
from typing import Dict, List, Mapping


class AHP(MCDA):
    def __init__(self, root_criterium: List[Criterium], criteria_comp: List[List], alter_comp: Mapping[str, List[List]], ranking_method: RankingMethod=RankingMethod.EVM):
        self.ranking_method = ranking_method
        self.root_criterium = root_criterium
        self.criteria_dict = dict()
        self.root_criterium.apply(lambda c: self.criteria_dict.update({c.id: c}))
        self.criteria_matrices = self._criteria_matrices(criteria_comp)
        self.alternatives_matrices = self._alternative_matrices(alter_comp)


    def _criteria_matrices(self, criteria_comp: List[List]) -> Mapping[str, ComprehensionMatrix]:
        sorted_comprehensions: Dict[List[List]] = {p.id: [] for p in self.criteria_dict.values() if not p.is_leaf}
        for com in criteria_comp:
            sorted_comprehensions[self.criteria_dict[com[0]].parent_criterium].append(com)
        return {parent_id: ComprehensionMatrix(comparisons, self.ranking_method) for parent_id, comparisons in sorted_comprehensions.items()}

    
    def _alternative_matrices(self, alter_comp: List[List]) -> Mapping[str, ComprehensionMatrix]:
        return {criteria_id: ComprehensionMatrix(comparisons, self.ranking_method) for criteria_id, comparisons in alter_comp.items()}


    def priority_of(self, c: Criterium) -> float:
        return 1 if c.parent_criterium is None else self.criteria_matrices[c.parent_criterium][c.id]


    def get_alternative_value(self, alternative:A, criterium:Criterium) -> float:
        return self.alternatives_matrices[criterium.id][alternative['id']]
