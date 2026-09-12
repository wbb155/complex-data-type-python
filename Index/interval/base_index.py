# base_index.py
from abc import ABC, abstractmethod
from typing import List
from trip import Trip

class BaseIndex(ABC):
    @abstractmethod
    def build(self, trips: List[Trip]) -> None:
        """index create"""
        pass

    @abstractmethod
    def snapshot_query(self, q: int) -> int:
        """return intervals include q"""
        pass

    @abstractmethod
    def interval_query(self, qs: int, qe: int) -> int:
        """interval query：return intervals intersact with qs,qe"""
        pass