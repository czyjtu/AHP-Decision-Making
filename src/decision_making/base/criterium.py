from dataclasses import dataclass, field
from typing import Sequence, Union


@dataclass(frozen=True)
class Criterium:
    id: Union[str, int] = field(repr=True, hash=True)
    higher_better: bool
    is_leaf: bool = field(init=False)
    is_root: bool = field(init=False)
    parent_criterium: Union[str, int] = field(default=None)
    sub_criteria: Sequence[Union[str, int]] = field(default_factory=list)

    def __post_init__(self):
        object.__setattr__(self, 'is_root', self.parent_criterium is None)
        object.__setattr__(self, 'is_leaf', len(self.sub_criteria) == 0) 
        


    