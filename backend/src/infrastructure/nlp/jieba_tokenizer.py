"""Jieba tokenizer implementation."""

import logging
from typing import List

from src.domain.ports.nlp.tokenizer import Token, Tokenizer

logger = logging.getLogger(__name__)


class JiebaTokenizer(Tokenizer):
    """Jieba-based Chinese tokenizer."""

    def __init__(self, user_dict_path: str = None):
        self._jieba = None
        self.user_dict_path = user_dict_path
        self._initialized = False

    def _init_jieba(self):
        """Lazy initialization of jieba."""
        if self._initialized:
            return
            
        try:
            import jieba
            import jieba.posseg as pseg
            
            self._jieba = jieba
            self._pseg = pseg
            
            if self.user_dict_path:
                jieba.load_userdict(self.user_dict_path)
                
            self._initialized = True
            logger.info("Jieba tokenizer initialized")
        except ImportError:
            logger.error("jieba not installed. Run: pip install jieba")
            raise

    def segment_sync(self, text: str) -> List[Token]:
        """Synchronous segmentation."""
        self._init_jieba()
        
        tokens = []
        for word, flag in self._pseg.cut(text):
            # Find position in original text
            start = text.find(word, tokens[-1].end if tokens else 0)
            end = start + len(word)
            
            tokens.append(Token(
                text=word,
                pos=flag,
                start=start,
                end=end
            ))
        
        return tokens

    async def segment(self, text: str) -> List[Token]:
        """Async segmentation (runs in thread pool)."""
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, self.segment_sync, text
        )
