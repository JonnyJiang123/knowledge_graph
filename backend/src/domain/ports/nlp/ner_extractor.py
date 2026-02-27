"""NER extractor port for named entity recognition."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class EntityMention:
    """A named entity mention found in text."""
    text: str
    label: str  # PERSON, ORGANIZATION, LOCATION, etc.
    start: int
    end: int
    confidence: float


class NERExtractor(ABC):
    """Abstract NER extractor for named entity recognition."""

    @abstractmethod
    async def extract(self, text: str) -> List[EntityMention]:
        """Extract named entities from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of entity mentions with confidence scores
        """
        ...

    @abstractmethod
    def extract_sync(self, text: str) -> List[EntityMention]:
        """Synchronous version of extract.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of entity mentions with confidence scores
        """
        ...

    @abstractmethod
    async def extract_batch(self, texts: List[str]) -> List[List[EntityMention]]:
        """Extract entities from multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of entity mentions for each text
        """
        ...
