"""Knowledge extraction service orchestrating NER and relation extraction."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from src.domain.entities.entity import Entity
from src.domain.entities.relation import Relation
from src.domain.ports.nlp.ner_extractor import EntityMention, NERExtractor
from src.domain.ports.nlp.tokenizer import Token, Tokenizer


@dataclass(frozen=True)
class RelationMention:
    """A relation mention between two entities."""
    source_text: str
    target_text: str
    relation_type: str
    confidence: float
    context: str = ""


@dataclass
class ExtractionResult:
    """Result of knowledge extraction from text."""
    entities: List[EntityMention] = field(default_factory=list)
    relations: List[RelationMention] = field(default_factory=list)
    tokens: List[Token] = field(default_factory=list)
    
    def merge(self, other: "ExtractionResult") -> "ExtractionResult":
        """Merge another extraction result into this one."""
        self.entities.extend(other.entities)
        self.relations.extend(other.relations)
        self.tokens.extend(other.tokens)
        return self


class RelationExtractor(ABC):
    """Abstract relation extractor."""

    @abstractmethod
    def extract(
        self, 
        text: str, 
        entities: List[EntityMention]
    ) -> List[RelationMention]:
        """Extract relations between entities in text.
        
        Args:
            text: Original text
            entities: Extracted entity mentions
            
        Returns:
            List of relation mentions
        """
        ...


class PatternBasedRelationExtractor(RelationExtractor):
    """Relation extractor based on patterns."""

    # Common relation patterns in Chinese
    PATTERNS = {
        "INVEST": [
            r"(\w+).*?投资.*?(\w+)",
            r"(\w+).*?持股.*?(\w+)",
            r"(\w+).*?控股.*?(\w+)",
        ],
        "WORK_FOR": [
            r"(\w+).*?就职于.*?(\w+)",
            r"(\w+).*?任职于.*?(\w+)",
            r"(\w+).*?加入.*?(\w+)",
        ],
        "FOUNDED": [
            r"(\w+).*?创立.*?(\w+)",
            r"(\w+).*?创办.*?(\w+)",
            r"(\w+).*?创建.*?(\w+)",
        ],
        "PARTNER": [
            r"(\w+).*?合作.*?(\w+)",
            r"(\w+).*?战略合作.*?(\w+)",
        ],
    }

    def extract(
        self, 
        text: str, 
        entities: List[EntityMention]
    ) -> List[RelationMention]:
        """Extract relations using predefined patterns."""
        relations = []
        entity_texts = {e.text for e in entities}
        
        for relation_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    source = match.group(1)
                    target = match.group(2)
                    
                    # Only create relation if both match entities
                    if source in entity_texts and target in entity_texts:
                        relations.append(RelationMention(
                            source_text=source,
                            target_text=target,
                            relation_type=relation_type,
                            confidence=0.7,
                            context=match.group(0)
                        ))
        
        return relations


class KnowledgeExtractor:
    """Orchestrates knowledge extraction from text."""

    def __init__(
        self,
        ner_extractor: NERExtractor,
        tokenizer: Optional[Tokenizer] = None,
        relation_extractor: Optional[RelationExtractor] = None,
    ):
        self.ner = ner_extractor
        self.tokenizer = tokenizer
        self.relation_extractor = relation_extractor or PatternBasedRelationExtractor()

    async def extract(self, text: str) -> ExtractionResult:
        """Extract knowledge (entities and relations) from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Extraction result with entities and relations
        """
        result = ExtractionResult()
        
        # Extract entities
        result.entities = await self.ner.extract(text)
        
        # Tokenize if tokenizer available
        if self.tokenizer:
            result.tokens = await self.tokenizer.segment(text)
        
        # Extract relations
        result.relations = self.relation_extractor.extract(text, result.entities)
        
        return result

    async def extract_batch(self, texts: List[str]) -> List[ExtractionResult]:
        """Extract knowledge from multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of extraction results
        """
        return [await self.extract(text) for text in texts]

    def extract_sync(self, text: str) -> ExtractionResult:
        """Synchronous extraction for small texts.
        
        Args:
            text: Input text
            
        Returns:
            Extraction result
        """
        import asyncio
        return asyncio.run(self.extract(text))

    def to_domain_entities(
        self, 
        mentions: List[EntityMention],
        project_id: str
    ) -> List[Entity]:
        """Convert entity mentions to domain entities.
        
        Args:
            mentions: Extracted entity mentions
            project_id: Project ID for the entities
            
        Returns:
            List of domain entities
        """
        entities = []
        for i, mention in enumerate(mentions):
            entity = Entity(
                project_id=project_id,
                external_id=f"auto-{mention.label}-{i}",
                type=mention.label.upper(),
                labels=[mention.label],
                properties={
                    "name": mention.text,
                    "confidence": mention.confidence,
                    "source": "auto-extraction"
                }
            )
            entities.append(entity)
        return entities
