"""Tests for knowledge extraction domain service."""

import pytest

from src.domain.services.extraction.knowledge_extractor import (
    ExtractionResult,
    KnowledgeExtractor,
    PatternBasedRelationExtractor,
    RelationMention,
)
from src.domain.ports.nlp.ner_extractor import EntityMention


class MockNERExtractor:
    """Mock NER extractor for testing."""
    
    async def extract(self, text: str):
        return [
            EntityMention("马云", "PERSON", 0, 2, 0.95),
            EntityMention("阿里巴巴", "ORGANIZATION", 5, 9, 0.92),
        ]


class TestPatternBasedRelationExtractor:
    """Tests for pattern-based relation extraction."""
    
    def test_extract_investment_relation(self):
        extractor = PatternBasedRelationExtractor()
        text = "马云投资阿里巴巴"
        entities = [
            EntityMention("马云", "PERSON", 0, 2, 0.95),
            EntityMention("阿里巴巴", "ORGANIZATION", 4, 8, 0.92),
        ]
        
        relations = extractor.extract(text, entities)
        
        assert len(relations) >= 1
        assert any(r.relation_type == "INVEST" for r in relations)
    
    def test_extract_founded_relation(self):
        extractor = PatternBasedRelationExtractor()
        text = "马云创立阿里巴巴"
        entities = [
            EntityMention("马云", "PERSON", 0, 2, 0.95),
            EntityMention("阿里巴巴", "ORGANIZATION", 4, 8, 0.92),
        ]
        
        relations = extractor.extract(text, entities)
        
        assert any(r.relation_type == "FOUNDED" for r in relations)


class TestKnowledgeExtractor:
    """Tests for knowledge extractor orchestrator."""
    
    @pytest.mark.asyncio
    async def test_extract_knowledge(self):
        ner = MockNERExtractor()
        extractor = KnowledgeExtractor(ner)
        
        result = await extractor.extract("马云投资阿里巴巴")
        
        assert isinstance(result, ExtractionResult)
        assert len(result.entities) == 2
        assert result.entities[0].text == "马云"
    
    def test_to_domain_entities(self):
        ner = MockNERExtractor()
        extractor = KnowledgeExtractor(ner)
        
        mentions = [
            EntityMention("马云", "PERSON", 0, 2, 0.95),
            EntityMention("阿里巴巴", "ORGANIZATION", 5, 9, 0.92),
        ]
        
        entities = extractor.to_domain_entities(mentions, "proj-1")
        
        assert len(entities) == 2
        assert entities[0].type == "PERSON"
        assert entities[1].type == "ORGANIZATION"
