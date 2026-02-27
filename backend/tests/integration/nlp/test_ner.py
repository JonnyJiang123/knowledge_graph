"""Integration tests for NER extractors."""

import pytest

from src.domain.ports.nlp.ner_extractor import EntityMention
from src.infrastructure.nlp.hanlp_ner import HanLPNERExtractor
from src.infrastructure.nlp.spacy_ner import SpacyNERExtractor


class TestHanLPNERExtractor:
    """Tests for HanLP NER extractor."""

    @pytest.fixture
    def extractor(self):
        return HanLPNERExtractor()

    @pytest.mark.asyncio
    async def test_extract_person_entity(self, extractor):
        text = "马云是阿里巴巴的创始人"
        entities = await extractor.extract(text)

        assert len(entities) >= 1
        person_entities = [e for e in entities if e.label == "PERSON"]
        assert any("马云" in e.text for e in person_entities)

    @pytest.mark.asyncio
    async def test_extract_organization_entity(self, extractor):
        text = "阿里巴巴是一家科技公司"
        entities = await extractor.extract(text)

        org_entities = [e for e in entities if e.label == "ORGANIZATION"]
        assert any("阿里巴巴" in e.text for e in org_entities)

    @pytest.mark.asyncio
    async def test_extract_returns_confidence(self, extractor):
        text = "北京市是中国的首都"
        entities = await extractor.extract(text)

        for entity in entities:
            assert 0.0 <= entity.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_extract_empty_text(self, extractor):
        entities = await extractor.extract("")
        assert entities == []


class TestSpacyNERExtractor:
    """Tests for spaCy NER extractor."""

    @pytest.fixture
    def extractor(self):
        return SpacyNERExtractor()

    @pytest.mark.asyncio
    async def test_extract_entities(self, extractor):
        text = "马云创立了阿里巴巴"
        entities = await extractor.extract(text)

        assert isinstance(entities, list)
        for entity in entities:
            assert isinstance(entity, EntityMention)
            assert entity.text
            assert entity.label
            assert entity.start >= 0
            assert entity.end > entity.start

    @pytest.mark.asyncio
    async def test_label_mapping(self, extractor):
        text = "张三在北京工作"
        entities = await extractor.extract(text)

        # Check that spaCy labels are mapped correctly
        labels = {e.label for e in entities}
        valid_labels = {"PERSON", "ORGANIZATION", "LOCATION", "GPE", "DATE", "TIME"}
        assert labels.issubset(valid_labels) or len(labels) == 0


class TestNERComparison:
    """Compare different NER extractors."""

    @pytest.mark.asyncio
    async def test_extractors_on_same_text(self):
        text = "马云是阿里巴巴的创始人"

        hanlp = HanLPNERExtractor()
        spacy = SpacyNERExtractor()

        hanlp_entities = await hanlp.extract(text)
        spacy_entities = await spacy.extract(text)

        # Both should return entities
        assert isinstance(hanlp_entities, list)
        assert isinstance(spacy_entities, list)

        # Check entity format
        for entities in [hanlp_entities, spacy_entities]:
            for entity in entities:
                assert hasattr(entity, 'text')
                assert hasattr(entity, 'label')
                assert hasattr(entity, 'start')
                assert hasattr(entity, 'end')
