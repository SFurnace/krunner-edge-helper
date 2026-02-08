"""
Pinyin Matcher - Chinese pinyin search support
"""
from typing import List, Tuple
from pypinyin import lazy_pinyin, Style


class PinyinMatcher:
    """Handles Chinese pinyin matching for search"""
    
    def __init__(self):
        self._pinyin_cache = {}
    
    def get_pinyin_variations(self, text: str) -> List[str]:
        """
        Get pinyin variations for Chinese text
        Returns: list of [full_pinyin, initials, original_text]
        """
        if text in self._pinyin_cache:
            return self._pinyin_cache[text]
        
        # Get full pinyin (e.g., "zhong guo")
        full_pinyin = ''.join(lazy_pinyin(text, style=Style.NORMAL))
        
        # Get pinyin initials (e.g., "zg")
        initials = ''.join(lazy_pinyin(text, style=Style.FIRST_LETTER))
        
        # Store variations
        variations = [
            text.lower(),           # Original text (lowercase)
            full_pinyin.lower(),    # Full pinyin
            initials.lower(),       # Pinyin initials
        ]
        
        # Also add space-separated full pinyin for better matching
        full_pinyin_spaced = ' '.join(lazy_pinyin(text, style=Style.NORMAL))
        if full_pinyin_spaced != full_pinyin:
            variations.append(full_pinyin_spaced.lower())
        
        self._pinyin_cache[text] = variations
        return variations
    
    def contains_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters"""
        return any('\u4e00' <= char <= '\u9fff' for char in text)
    
    def match_with_pinyin(self, text: str, query: str) -> bool:
        """
        Check if query matches text (with pinyin support)
        Returns True if query matches any pinyin variation of text
        """
        query = query.lower()
        
        # Direct match
        if query in text.lower():
            return True
        
        # If text contains Chinese, check pinyin variations
        if self.contains_chinese(text):
            variations = self.get_pinyin_variations(text)
            return any(query in variation for variation in variations)
        
        return False
    
    def score_match(self, text: str, query: str) -> int:
        """
        Score how well the query matches the text with pinyin
        Returns score 0-100, higher is better
        Pinyin matching has higher priority
        """
        query = query.lower()
        text_lower = text.lower()
        
        # Check pinyin matches first if contains Chinese
        if self.contains_chinese(text):
            variations = self.get_pinyin_variations(text)
            
            for i, variation in enumerate(variations):
                # Exact match with pinyin variation
                if query == variation:
                    return 95 - (i * 3)
                # Starts with pinyin variation (prefix match)
                elif variation.startswith(query):
                    return 88 - (i * 3)
                # Contains query in pinyin variation (substring match)
                elif query in variation:
                    return 75 - (i * 3)
        
        # Fallback to original text match (lower priority than pinyin)
        # Exact match with original text
        if query == text_lower:
            return 100
        
        # Starts with query (original text)
        if text_lower.startswith(query):
            return 85
        
        return 0
