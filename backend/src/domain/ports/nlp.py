"""NLP (Natural Language Processing) ports - Abstract interfaces for NLP adapters.

This module defines the abstract interfaces (ports) that the domain layer uses
for natural language processing operations. Concrete implementations (adapters)
are provided in the infrastructure layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class Token:
    """A token represents a segmented unit of text with part-of-speech information.
    
    Attributes:
        text: The text content of the token.
        pos: Part of speech tag (e.g., 'n' for noun, 'v' for verb).
        start: Start position (character index) in the original text.
        end: End position (character index) in the original text.
    """
    text: str
    pos: str
    start: int
    end: int


@dataclass(frozen=True)
class EntityMention:
    """An entity mention extracted from text.
    
    Attributes:
        text: The text content of the entity mention.
        label: Entity type label (e.g., 'PERSON', 'ORG', 'LOC').
        start: Start position (character index) in the original text.
        end: End position (character index) in the original text.
        confidence: Confidence score (0.0 to 1.0).
    """
    text: str
    label: str
    start: int
    end: int
    confidence: float


@dataclass(frozen=True)
class RelationMention:
    """A relation mention between two entities extracted from text.
    
    Attributes:
        source_text: Text of the source entity.
        target_text: Text of the target entity.
        relation_type: Type of relation (e.g., 'WORKS_FOR', 'LOCATED_IN').
        confidence: Confidence score (0.0 to 1.0).
        evidence: Optional text snippet showing the relation context.
    """
    source_text: str
    target_text: str
    relation_type: str
    confidence: float
    evidence: Optional[str] = None


class Tokenizer(ABC):
    """Abstract port for text tokenization.
    
    Implementations should handle word segmentation and part-of-speech tagging
    for the target language (e.g., Chinese, English).
    """
    
    @abstractmethod
    async def tokenize(self, text: str) -> list[Token]:
        """Tokenize the input text into a list of tokens.
        
        Args:
            text: The input text to tokenize.
            
        Returns:
            A list of Token objects with text, POS tags, and positions.
            
        Raises:
            NLPPipelineError: If tokenization fails.
        """
        ...
    
    @abstractmethod
    def tokenize_sync(self, text: str) -> list[Token]:
        """Synchronous version of tokenize for non-async contexts.
        
        Args:
            text: The input text to tokenize.
            
        Returns:
            A list of Token objects with text, POS tags, and positions.
        """
        ...


class NERExtractor(ABC):
    """Abstract port for Named Entity Recognition.
    
    Implementations should identify and classify named entities in text,
    such as persons, organizations, locations, etc.
    """
    
    @abstractmethod
    async def extract_entities(self, text: str) -> list[EntityMention]:
        """Extract named entities from the input text.
        
        Args:
            text: The input text to analyze.
            
        Returns:
            A list of EntityMention objects.
            
        Raises:
            NLPPipelineError: If entity extraction fails.
        """
        ...
    
    @abstractmethod
    def extract_entities_sync(self, text: str) -> list[EntityMention]:
        """Synchronous version of extract_entities for non-async contexts.
        
        Args:
            text: The input text to analyze.
            
        Returns:
            A list of EntityMention objects.
        """
        ...
    
    @property
    @abstractmethod
    def supported_labels(self) -> set[str]:
        """Return the set of entity labels supported by this extractor.
        
        Returns:
            A set of label strings (e.g., {'PERSON', 'ORG', 'LOC'}).
        """
        ...


class RelationExtractor(ABC):
    """Abstract port for Relation Extraction.
    
    Implementations should identify semantic relationships between
    entities mentioned in text.
    """
    
    @abstractmethod
    async def extract_relations(
        self,
        text: str,
        entities: list[EntityMention],
    ) -> list[RelationMention]:
        """Extract relations between entities in the input text.
        
        Args:
            text: The original input text.
            entities: List of entities already extracted from the text.
            
        Returns:
            A list of RelationMention objects.
            
        Raises:
            NLPPipelineError: If relation extraction fails.
        """
        ...
    
    @abstractmethod
    def extract_relations_sync(
        self,
        text: str,
        entities: list[EntityMention],
    ) -> list[RelationMention]:
        """Synchronous version of extract_relations for non-async contexts.
        
        Args:
            text: The original input text.
            entities: List of entities already extracted from the text.
            
        Returns:
            A list of RelationMention objects.
        """
        ...


class NLPPipeline(ABC):
    """Abstract port for a complete NLP pipeline.
    
    Combines tokenization, NER, and relation extraction into a unified interface.
    """
    
    @abstractmethod
    async def process(self, text: str) -> dict[str, Any]:
        """Process text through the complete NLP pipeline.
        
        Args:
            text: The input text to process.
            
        Returns:
            A dictionary containing:
                - 'tokens': list of Token objects
                - 'entities': list of EntityMention objects
                - 'relations': list of RelationMention objects
        """
        ...


class NLPPipelineError(Exception):
    """Base exception for NLP pipeline errors."""
    
    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.cause = cause
        self.message = message


class ModelLoadError(NLPPipelineError):
    """Exception raised when an NLP model fails to load."""
    pass


class ProcessingError(NLPPipelineError):
    """Exception raised when text processing fails."""
    pass
