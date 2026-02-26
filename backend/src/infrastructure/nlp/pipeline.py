"""Default NLP Pipeline implementation.

This module provides a concrete implementation of the NLPPipeline port
that combines tokenizer, NER, and relation extractor components.
"""

from __future__ import annotations

import logging
from typing import Any

from src.domain.ports.nlp import (
    EntityMention,
    NLPPipeline,
    NLPPipelineError,
    NERExtractor,
    RelationExtractor,
    RelationMention,
    Token,
    Tokenizer,
)

logger = logging.getLogger(__name__)


class DefaultNLPPipeline(NLPPipeline):
    """Default implementation of the NLP pipeline.
    
    Combines a tokenizer, NER extractor, and relation extractor into
    a unified processing pipeline.
    
    Args:
        tokenizer: The tokenizer component.
        ner: The named entity recognition component.
        relation_extractor: The relation extraction component.
    
    Example:
        >>> pipeline = DefaultNLPPipeline(
        ...     tokenizer=JiebaTokenizer(),
        ...     ner=HanlpNER(),
        ...     relation_extractor=PatternBasedRelationExtractor(),
        ... )
        >>> result = await pipeline.process("马云创立了阿里巴巴")
        >>> print(result['entities'])
    """
    
    def __init__(
        self,
        tokenizer: Tokenizer,
        ner: NERExtractor,
        relation_extractor: RelationExtractor,
    ) -> None:
        self._tokenizer = tokenizer
        self._ner = ner
        self._relation_extractor = relation_extractor
        logger.debug(
            "Initialized DefaultNLPPipeline with tokenizer=%s, ner=%s, relation_extractor=%s",
            type(tokenizer).__name__,
            type(ner).__name__,
            type(relation_extractor).__name__,
        )
    
    async def process(self, text: str) -> dict[str, Any]:
        """Process text through the complete NLP pipeline.
        
        Args:
            text: The input text to process.
            
        Returns:
            A dictionary containing:
                - 'tokens': list of Token objects
                - 'entities': list of EntityMention objects
                - 'relations': list of RelationMention objects
                
        Raises:
            NLPPipelineError: If any processing step fails.
        """
        if not text or not text.strip():
            return {
                'tokens': [],
                'entities': [],
                'relations': [],
            }
        
        try:
            # Step 1: Tokenization
            logger.debug("Starting tokenization for text length=%d", len(text))
            tokens = await self._tokenizer.tokenize(text)
            logger.debug("Tokenization completed: %d tokens", len(tokens))
            
            # Step 2: Named Entity Recognition
            logger.debug("Starting NER extraction")
            entities = await self._ner.extract_entities(text)
            logger.debug("NER completed: %d entities found", len(entities))
            
            # Step 3: Relation Extraction
            logger.debug("Starting relation extraction")
            relations = await self._relation_extractor.extract_relations(text, entities)
            logger.debug("Relation extraction completed: %d relations found", len(relations))
            
            return {
                'tokens': tokens,
                'entities': entities,
                'relations': relations,
            }
            
        except NLPPipelineError:
            raise
        except Exception as e:
            logger.exception("NLP pipeline processing failed")
            raise NLPPipelineError(f"Pipeline processing failed: {e}", cause=e) from e
    
    def process_sync(self, text: str) -> dict[str, Any]:
        """Synchronous version of process for non-async contexts.
        
        Args:
            text: The input text to process.
            
        Returns:
            A dictionary containing tokens, entities, and relations.
        """
        if not text or not text.strip():
            return {
                'tokens': [],
                'entities': [],
                'relations': [],
            }
        
        try:
            # Step 1: Tokenization
            tokens = self._tokenizer.tokenize_sync(text)
            
            # Step 2: Named Entity Recognition
            entities = self._ner.extract_entities_sync(text)
            
            # Step 3: Relation Extraction
            relations = self._relation_extractor.extract_relations_sync(text, entities)
            
            return {
                'tokens': tokens,
                'entities': entities,
                'relations': relations,
            }
            
        except NLPPipelineError:
            raise
        except Exception as e:
            logger.exception("NLP pipeline processing failed")
            raise NLPPipelineError(f"Pipeline processing failed: {e}", cause=e) from e
