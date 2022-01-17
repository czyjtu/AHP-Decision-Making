from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union, List, Callable


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

    def apply(self, fun: Callable[[Criterium], None]) -> None:
        fun(self)
        list(map(fun, self.sub_criteria))

    def add_subcriterium(self, subcriterium: Criterium) -> None:
        if subcriterium in self.sub_criteria:
            raise ValueError(f"Subcriterium {subcriterium.id} alredy in subcriteria list")
        if subcriterium.parent_criterium is not None:
            raise ValueError(
                f"Given subcriterium {subcriterium.id} already has a parent criterium '{subcriterium.parent_criterium}'"
            )
        self.sub_criteria.append(subcriterium)
        subcriterium.parent_criterium = self
        self.is_leaf = False


