"""The stored Trip relation (id, start, end) and its catalog statistics."""

import os

from trip import Trip

from .catalog import Field, Schema, TableStats

_ID, _START, _END = "Trip.ID", "Trip.start", "Trip.end"


class TripRelation:
    """A heap relation holding the three integer Trip columns.

    Columns are kept as numpy arrays when pandas is available (fast bulk load),
    otherwise as plain Python lists; iteration converts to Python ints lazily.
    """

    COLUMNS = (_ID, _START, _END)

    def __init__(self, ids, starts, ends):
        self.ids = ids
        self.starts = starts
        self.ends = ends
        self.schema = Schema((
            Field("id", "int"),
            Field("start", "int"),
            Field("end", "int"),
        ))
        self.stats = self._compute_stats()

    # --------------------------------------------------------------- loading
    @classmethod
    def load(cls, path: str) -> "TripRelation":
        ext = os.path.splitext(path)[1].lower()
        if ext == ".parquet":
            ids, starts, ends = cls._load_parquet(path)
        else:
            ids, starts, ends = cls._load_csv(path)
        return cls(ids, starts, ends)

    @staticmethod
    def _load_parquet(path):
        import pandas as pd  # heavy dependency, imported only when needed
        df = pd.read_parquet(path, columns=[_ID, _START, _END])
        return df[_ID].to_numpy(), df[_START].to_numpy(), df[_END].to_numpy()

    @staticmethod
    def _load_csv(path):
        try:
            import pandas as pd
            df = pd.read_csv(path)
            return df[_ID].to_numpy(), df[_START].to_numpy(), df[_END].to_numpy()
        except ImportError:
            import csv
            ids, starts, ends = [], [], []
            with open(path, newline="") as fh:
                for row in csv.DictReader(fh):
                    ids.append(int(row[_ID]))
                    starts.append(int(row[_START]))
                    ends.append(int(row[_END]))
            return ids, starts, ends

    # ---------------------------------------------------------------- catalog
    def _compute_stats(self) -> TableStats:
        starts, ends = self.starts, self.ends
        if len(starts) == 0:
            return TableStats(row_count=0)
        return TableStats(
            row_count=len(starts),
            col_min={"start": int(min(starts)), "end": int(min(ends))},
            col_max={"start": int(max(starts)), "end": int(max(ends))},
        )

    def __len__(self):
        return len(self.ids)

    # ------------------------------------------------------------- scan access
    def iter_trips(self):
        """Full table scan producing Trip tuples, as the IT build consumes."""
        ids, starts, ends = self.ids, self.starts, self.ends
        for i in range(len(ids)):
            yield Trip(int(ids[i]), int(starts[i]), int(ends[i]))
