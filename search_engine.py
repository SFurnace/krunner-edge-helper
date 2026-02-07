"""
Search Engine for Edge Bookmarks
Combines fuzzy search and pinyin matching
"""
from typing import List, Tuple
from rapidfuzz import fuzz
from bookmark_parser import Bookmark
from pinyin_matcher import PinyinMatcher
import config


class SearchEngine:
    """Fuzzy search engine with pinyin support"""
    
    def __init__(self):
        self.pinyin_matcher = PinyinMatcher()
    
    def search(self, bookmarks: List[Bookmark], query: str) -> List[Tuple[Bookmark, int]]:
        """
        Search bookmarks with fuzzy and pinyin matching
        Returns: List of (bookmark, score) tuples sorted by score descending
        """
        if not query:
            return []
        
        results = []
        query = query.strip()
        
        for bookmark in bookmarks:
            score = self._calculate_score(bookmark, query)
            
            if score >= config.FUZZY_THRESHOLD:
                results.append((bookmark, score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Limit results
        return results[:config.MAX_RESULTS]
    
    def _calculate_score(self, bookmark: Bookmark, query: str) -> int:
        """Calculate relevance score for a bookmark"""
        
        # Score based on name (weighted higher)
        name_score = self._score_text(bookmark.name, query)
        
        # Score based on URL (weighted lower)
        url_score = self._score_text(bookmark.url, query) * 0.5
        
        # Score based on folder (weighted lowest)
        folder_score = self._score_text(bookmark.folder, query) * 0.3
        
        # Combined score
        total_score = max(name_score, url_score, folder_score)
        
        return int(total_score)
    
    def _score_text(self, text: str, query: str) -> float:
        """Score how well query matches text"""
        if not text:
            return 0
        
        query = query.lower()
        text_lower = text.lower()
        
        # Try pinyin matching first (if text contains Chinese)
        if self.pinyin_matcher.contains_chinese(text):
            pinyin_score = self.pinyin_matcher.score_match(text, query)
            if pinyin_score > 0:
                return float(pinyin_score)
        
        # Exact match
        if query == text_lower:
            return 100.0
        
        # Substring match
        if query in text_lower:
            # Score based on position (earlier is better)
            position = text_lower.index(query)
            position_penalty = min(position * 2, 30)
            return 90.0 - position_penalty
        
        # Fuzzy matching
        # Use token_set_ratio for better partial matching
        fuzzy_score = fuzz.token_set_ratio(query, text_lower)
        
        # Also try partial ratio
        partial_score = fuzz.partial_ratio(query, text_lower)
        
        return max(fuzzy_score, partial_score)
