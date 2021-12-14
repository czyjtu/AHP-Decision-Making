from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence, Union, List, Callable


@dataclass
class Criterium:
    id: str = field(repr=True, hash=True)
    sub_criteria: List[Criterium] = field(default_factory=list)
    higher_better: bool = True
    is_leaf: bool = field(init=False)
    parent_criterium: Union[str, int] = field(init=False, default=None)
    
    def __post_init__(self):
        self.is_leaf = len(self.sub_criteria) == 0
        for sub in self.sub_criteria:
            sub.parent_criterium = self.id

    def apply(self, fun: Callable[[Criterium], None]):
        fun(self)
        list(map(fun, self.sub_criteria))
        


    