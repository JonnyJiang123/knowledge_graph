"""NLP adapters for knowledge extraction."""

try:
    from .jieba_tokenizer import JiebaTokenizer
except ImportError:
    JiebaTokenizer = None

try:
    from .hanlp_ner import HanLPNERExtractor
except ImportError:
    HanLPNERExtractor = None

try:
    from .spacy_ner import SpacyNERExtractor
except ImportError:
    SpacyNERExtractor = None

from .relation_extractor import DependencyRelationExtractor

__all__ = [
    "JiebaTokenizer",
    "HanLPNERExtractor", 
    "SpacyNERExtractor",
    "DependencyRelationExtractor",
]
