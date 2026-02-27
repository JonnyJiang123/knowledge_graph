"""Tokenizer port for text segmentation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Token:
    """A token from text segmentation."""
    text: str
    pos: str  # part of speech
    start: int
    end: int


class Tokenizer(ABC):
    """Abstract tokenizer for text segmentation."""

    @abstractmethod
    async def segment(self, text: str) -> List[Token]:
        """Segment text into tokens.
        
        Args:
            text: Input text to segment
            
        Returns:
            List of tokens with position info
        """
        ...

    @abstractmethod
    def segment_sync(self, text: str) -> List[Token]:
        """Synchronous version of segment.
        
        Args:
            text: Input text to segment
            
        Returns:
            List of tokens with position info
        """
        ...
