"""System catalogs: schema, statistics and the access-method registry."""

from dataclasses import dataclass, field
from typing import Callable, Dict, Tuple


@dataclass(frozen=True)
class Field:
    name: str
    type: str


@dataclass
class Schema:
    fields: Tuple[Field, ...]

    def names(self):
        return tuple(f.name for f in self.fields)


@dataclass
class TableStats:
    """Column-level statistics maintained by the catalog, like pg_statistic."""
    row_count: int = 0
    col_min: Dict[str, int] = field(default_factory=dict)
    col_max: Dict[str, int] = field(default_factory=dict)

    def domain_length(self, start_col="start", end_col="end") -> int:
        """max(end) - min(start): the length used to size query intervals."""
        if self.row_count == 0:
            return 0
        return self.col_max[end_col] - self.col_min[start_col]


class AccessMethodRegistry:
    """Registry of physical access methods (pg_am style).

    An access method is created for a relation and is responsible for building
    itself and answering snapshot / interval queries.
    """

    def __init__(self):
        self._factories: Dict[str, Callable] = {}

    def register(self, name: str, factory: Callable) -> None:
        self._factories[name] = factory

    def create(self, name: str, relation):
        return self._factories[name](relation)

    def names(self):
        return list(self._factories)
