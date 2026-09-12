# Trip.py
from dataclasses import dataclass
# It seems that interval is not a suitable name
# python interpret views it as a module
@dataclass
class Trip:
    id: int
    start: int   # seconds
    end: int
