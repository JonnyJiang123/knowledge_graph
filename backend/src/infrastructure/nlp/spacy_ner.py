"""spaCy NER extractor implementation (alternative)."""

import logging
from typing import List

from src.domain.ports.nlp.ner_extractor import EntityMention, NERExtractor

logger = logging.getLogger(__name__)


class SpacyNERExtractor(NERExtractor):
    """spaCy-based NER extractor (alternative for Chinese)."""

    # Label mapping from spaCy to our schema
    LABEL_MAP = {
        "PERSON": "PERSON",
        "PER": "PERSON",
        "ORG": "ORGANIZATION",
        "ORGANIZATION": "ORGANIZATION",
        "GPE": "LOCATION",
        "LOC": "LOCATION",
        "LOCATION": "LOCATION",
        "DATE": "DATE",
        "TIME": "TIME",
        "MONEY": "MONEY",
        "PERCENT": "PERCENT",
    }

    def __init__(self, model: str = "zh_core_web_sm"):
        self.model_name = model
        self._nlp = None
        self._initialized = False

    def _init_spacy(self):
        """Lazy initialization of spaCy."""
        if self._initialized:
            return
            
        try:
            import spacy
            
            self._nlp = spacy.load(self.model_name)
            self._initialized = True
            logger.info(f"spaCy NER initialized with model: {self.model_name}")
        except ImportError:
            logger.error("spacy not installed. Run: pip install spacy")
            raise
        except OSError:
            logger.error(f"spaCy model {self.model_name} not found. Run: python -m spacy download {self.model_name}")
            raise

    def _map_label(self, label: str) -> str:
        """Map spaCy label to our schema."""
        return self.LABEL_MAP.get(label, label)

    def extract_sync(self, text: str) -> List[EntityMention]:
        """Synchronous NER extraction."""
        self._init_spacy()
        
        doc = self._nlp(text)
        
        entities = []
        for ent in doc.ents:
            entities.append(EntityMention(
                text=ent.text,
                label=self._map_label(ent.label_),
                start=ent.start_char,
                end=ent.end_char,
                confidence=0.85
            ))
        
        return entities

    async def extract(self, text: str) -> List[EntityMention]:
        """Async NER extraction."""
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, self.extract_sync, text
        )

    async def extract_batch(self, texts: List[str]) -> List[List[EntityMention]]:
        """Extract entities from multiple texts."""
        return [await self.extract(text) for text in texts]
