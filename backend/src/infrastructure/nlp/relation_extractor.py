"""Advanced relation extractors."""

import logging
import re
from typing import List, Optional, Tuple

from src.domain.ports.nlp.ner_extractor import EntityMention
from src.domain.services.extraction.knowledge_extractor import (
    RelationExtractor,
    RelationMention,
)

logger = logging.getLogger(__name__)


class DependencyRelationExtractor(RelationExtractor):
    """Relation extractor using dependency parsing."""

    # Key verbs that indicate relations
    RELATION_VERBS = {
        "投资": "INVEST",
        "控股": "INVEST",
        "持股": "INVEST",
        "收购": "ACQUIRE",
        "合并": "MERGE",
        "合作": "PARTNER",
        "战略": "PARTNER",
        "创立": "FOUNDED",
        "创办": "FOUNDED",
        "创建": "FOUNDED",
        "成立": "FOUNDED",
        "任职": "WORK_FOR",
        "就职": "WORK_FOR",
        "加入": "WORK_FOR",
        "担任": "WORK_FOR",
    }

    def __init__(self, use_pos: bool = True):
        self.use_pos = use_pos
        self._nlp = None
        self._initialized = False

    def _init_spacy(self):
        """Initialize spaCy for dependency parsing."""
        if self._initialized:
            return
            
        try:
            import spacy
            self._nlp = spacy.load("zh_core_web_sm")
            self._initialized = True
            logger.info("Dependency parser initialized")
        except Exception as e:
            logger.warning(f"Failed to load spaCy for dependency parsing: {e}")
            self.use_pos = False

    def _extract_with_patterns(
        self, 
        text: str, 
        entities: List[EntityMention]
    ) -> List[RelationMention]:
        """Extract relations using patterns (fallback method)."""
        relations = []
        entity_texts = {e.text for e in entities}
        
        # Simple pattern: EntityA + Verb + EntityB
        for verb, rel_type in self.RELATION_VERBS.items():
            # Pattern: Entity Verb Entity
            pattern = rf"(\w{{2,20}})[^。]*?{verb}[^。]*?(\w{{2,20}})"
            matches = re.finditer(pattern, text)
            
            for match in matches:
                source = match.group(1)
                target = match.group(2)
                
                # Check if matched texts are entities
                source_entity = self._find_entity(source, entities)
                target_entity = self._find_entity(target, entities)
                
                if source_entity and target_entity:
                    relations.append(RelationMention(
                        source_text=source_entity.text,
                        target_text=target_entity.text,
                        relation_type=rel_type,
                        confidence=0.6,
                        context=match.group(0)
                    ))
        
        return relations

    def _find_entity(
        self, 
        text: str, 
        entities: List[EntityMention]
    ) -> Optional[EntityMention]:
        """Find an entity that matches the text."""
        for entity in entities:
            if entity.text in text or text in entity.text:
                return entity
        return None

    def _extract_with_dependencies(
        self, 
        text: str, 
        entities: List[EntityMention]
    ) -> List[RelationMention]:
        """Extract relations using dependency parsing."""
        if not self.use_pos or not self._nlp:
            return []
        
        doc = self._nlp(text)
        relations = []
        
        # Build entity span mapping
        entity_spans = {}
        for ent in entities:
            for token in doc:
                if token.idx >= ent.start and token.idx < ent.end:
                    entity_spans[token.i] = ent
        
        # Find relations through dependency paths
        for token in doc:
            if token.text in self.RELATION_VERBS:
                rel_type = self.RELATION_VERBS[token.text]
                
                # Find subject and object
                subj = None
                obj = None
                
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubj:pass"):
                        subj = self._find_entity_in_tree(child, entity_spans)
                    elif child.dep_ in ("dobj", "obj", "iobj"):
                        obj = self._find_entity_in_tree(child, entity_spans)
                
                if subj and obj:
                    relations.append(RelationMention(
                        source_text=subj.text,
                        target_text=obj.text,
                        relation_type=rel_type,
                        confidence=0.75,
                        context=token.sent.text if token.sent else ""
                    ))
        
        return relations

    def _find_entity_in_tree(
        self, 
        token, 
        entity_spans: dict
    ) -> Optional[EntityMention]:
        """Find entity mention in dependency tree."""
        # Check if token is part of an entity
        if token.i in entity_spans:
            return entity_spans[token.i]
        
        # Check children
        for child in token.children:
            result = self._find_entity_in_tree(child, entity_spans)
            if result:
                return result
        
        return None

    def extract(
        self, 
        text: str, 
        entities: List[EntityMention]
    ) -> List[RelationMention]:
        """Extract relations using dependency parsing with pattern fallback."""
        if not entities or len(entities) < 2:
            return []
        
        # Try dependency parsing if available
        if self.use_pos:
            self._init_spacy()
            dep_relations = self._extract_with_dependencies(text, entities)
            if dep_relations:
                return dep_relations
        
        # Fallback to pattern matching
        return self._extract_with_patterns(text, entities)


class LLMRelationExtractor(RelationExtractor):
    """Relation extractor using LLM (for future implementation)."""
    
    def __init__(self, model_endpoint: str = None):
        self.model_endpoint = model_endpoint
    
    def extract(
        self, 
        text: str, 
        entities: List[EntityMention]
    ) -> List[RelationMention]:
        """Extract relations using LLM (placeholder)."""
        # TODO: Implement LLM-based extraction
        logger.warning("LLM extractor not implemented yet")
        return []
