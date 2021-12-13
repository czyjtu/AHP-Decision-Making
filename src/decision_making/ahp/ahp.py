import numpy as np
from src.decision_making.ahp.utils import choice_list2matrix, comp_list2matrix
from src.decision_making.ahp.comparison_matrix import ComprehensionMatrix
from src.decision_making.base import MCDA, A, Preference, Criterium
from typing import Dict, List, Mapping


class AHP(MCDA):
    def __init__(self, criteria: List[Criterium], alternative_list: List[Dict], criteria_comp: List[List], alter_comp: Mapping[str, List[List]]):
        self.criteria = criteria
        self.criteria_dict: Dict[Criterium] = {cr.id: cr for cr in criteria}
        self.criteria_matrices = self._criteria_matrices(criteria_comp)
        self.alternatives_matrices = self._alternative_matrices(alter_comp) 
         # self.CRs = {ids: matrix.CR() for ids, matrix in self.matrices.items()}


        
    def _criteria_matrices(self, criteria_comp: List[List]) -> Mapping[str, ComprehensionMatrix]:
        sorted_comprehensions: Dict[List[List]] = {p.id: [] for p in self.criteria if not p.is_leaf}
        for com in criteria_comp:
            sorted_comprehensions[self.criteria_dict[com[0]].parent_criterium].append(com)
        return {parent_id: ComprehensionMatrix(comparisons) for parent_id, comparisons in sorted_comprehensions.items()}

    
    def _alternative_matrices(self, alter_comp: List[List]) -> Mapping[str, ComprehensionMatrix]:
        return {criteria_id: ComprehensionMatrix(comparisons) for criteria_id, comparisons in alter_comp.items()}


    def priority_of(self, c: Criterium) -> float:
        return 1 if c.is_root else self.criteria_matrices[c.parent_criterium][c.id]


    def get_alternative_value(self, alternative:A, criterium:Criterium) -> float:
        return self.alternatives_matrices[criterium.id][alternative['id']]
