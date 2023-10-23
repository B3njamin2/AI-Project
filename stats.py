from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(slots=True)
class Stats:
    """Representation of the global game statistics."""
    evaluations_per_depth : dict[int,int] = field(default_factory=dict)
    total_seconds: float = 0.0
    branching_factor: list[int] = field(default_factory=lambda: [0, 0]) 
    heuristic_score: float = 0.0