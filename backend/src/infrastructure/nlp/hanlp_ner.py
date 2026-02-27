"""HanLP NER extractor implementation."""

import logging
from typing import List

from src.domain.ports.nlp.ner_extractor import EntityMention, NERExtractor

logger = logging.getLogger(__name__)


class HanLPNERExtractor(NERExtractor):
    """HanLP-based NER extractor (primary Chinese NER)."""

    # Label mapping from HanLP to our schema
    LABEL_MAP = {
        "PERSON": "PERSON",
        "nr": "PERSON",
        "ORGANIZATION": "ORGANIZATION",
        "nt": "ORGANIZATION",
        "ns": "LOCATION",
        "LOCATION": "LOCATION",
        "GPE": "LOCATION",
        "DATE": "DATE",
        "TIME": "TIME",
        "MONEY": "MONEY",
        "PERCENT": "PERCENT",
    }

    def __init__(self, model_name: str = "MSRA_NER_BERT_BASE"):
        self.model_name = model_name
        self._pipeline = None
        self._initialized = False

    def _init_hanlp(self):
        """Lazy initialization of HanLP."""
        if self._initialized:
            return
            
        try:
            import hanlp
            
            # Load NER pipeline
            self._pipeline = hanlp.load(hanlp.pretrained.ner.MSRA_NER_BERT_BASE)
            self._initialized = True
            logger.info(f"HanLP NER initialized with model: {self.model_name}")
        except ImportError:
            logger.error("hanlp not installed. Run: pip install hanlp")
            raise
        except Exception as e:
            logger.error(f"Failed to load HanLP model: {e}")
            raise

    def _map_label(self, label: str) -> str:
        """Map HanLP label to our schema."""
        return self.LABEL_MAP.get(label, label)

    def extract_sync(self, text: str) -> List[EntityMention]:
        """Synchronous NER extraction."""
        self._init_hanlp()
        
        try:
            # Run NER
            results = self._pipeline(text)
            
            entities = []
            for item in results:
                if isinstance(item, tuple):
                    # (entity_text, label, start, end)
                    entity_text, label, start, end = item
                    entities.append(EntityMention(
                        text=entity_text,
                        label=self._map_label(label),
                        start=start,
                        end=end,
                        confidence=0.9
                    ))
                else:
                    # Handle different output format
                    entity_text = item.get("text", "")
                    label = item.get("label", "UNKNOWN")
                    start = item.get("start", 0)
                    end = item.get("end", len(entity_text))
                    confidence = item.get("confidence", 0.8)
                    
                    entities.append(EntityMention(
                        text=entity_text,
                        label=self._map_label(label),
                        start=start,
                        end=end,
                        confidence=confidence
                    ))
            
            return entities
            
        except Exception as e:
            logger.error(f"NER extraction failed: {e}")
            return []

    async def extract(self, text: str) -> List[EntityMention]:
        """Async NER extraction."""
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, self.extract_sync, text
        )

    async def extract_batch(self, texts: List[str]) -> List[List[EntityMention]]:
        """Extract entities from multiple texts."""
        return [await self.extract(text) for text in texts]
