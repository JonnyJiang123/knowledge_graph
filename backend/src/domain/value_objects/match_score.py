"""Match score value object with validation."""

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class MatchScore:
    """A match score between 0 and 1.
    
    Immutable value object that validates score is in valid range.
    """
    value: float

    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"MatchScore must be between 0 and 1, got {self.value}")

    @classmethod
    def from_string(cls, s: str) -> "MatchScore":
        """Create from string representation."""
        return cls(float(s))

    def __float__(self) -> float:
        return self.value

    def __lt__(self, other: Union["MatchScore", float]) -> bool:
        other_val = other.value if isinstance(other, MatchScore) else other
        return self.value < other_val

    def __le__(self, other: Union["MatchScore", float]) -> bool:
        other_val = other.value if isinstance(other, MatchScore) else other
        return self.value <= other_val

    def __gt__(self, other: Union["MatchScore", float]) -> bool:
        other_val = other.value if isinstance(other, MatchScore) else other
        return self.value > other_val

    def __ge__(self, other: Union["MatchScore", float]) -> bool:
        other_val = other.value if isinstance(other, MatchScore) else other
        return self.value >= other_val
