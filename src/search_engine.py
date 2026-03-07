"""
Search Engine for Edge Bookmarks
Combines text matching, pinyin matching, and history-based ranking
"""
from typing import List, Tuple
from bookmark_parser import Bookmark
from pinyin_matcher import PinyinMatcher
import config

# Import history manager if enabled
if config.HISTORY_ENABLED:
    from history_manager import HistoryManager


class SearchEngine:
    """Fuzzy search engine with pinyin and history support"""

    def __init__(self):
        self.pinyin_matcher = PinyinMatcher()
        self.history_manager = HistoryManager() if config.HISTORY_ENABLED else None
    
    def search(self, bookmarks: List[Bookmark], query: str) -> List[Tuple[Bookmark, float]]:
        """
        Search bookmarks with multi-keyword matching, pinyin, and history support
        Returns: List of (bookmark, score) tuples sorted by score descending
        """
        if not query:
            return []

        results = []
        original_query = query.strip()

        # Split query into keywords by space
        keywords = [kw.strip() for kw in original_query.split() if kw.strip()]

        for bookmark in bookmarks:
            base_score = self._calculate_score(bookmark, keywords)

            # Calculate final score: base score (capped at 80) + history bonus (max 20)
            # Base similarity contributes up to 80 points, history contributes up to 20 points
            history_weight = self.history_manager.get_weight(original_query, bookmark.url) if self.history_manager else 0.0
            base_component = min(base_score, 80)  # Cap base score at 80
            history_component = history_weight * config.HISTORY_SCORE_MAX  # History contributes max 20 points
            final_score = base_component + history_component

            # Include results that meet threshold OR have strong history
            if final_score >= config.FUZZY_THRESHOLD:
                results.append((bookmark, final_score))
            elif base_score > 0 and history_weight >= config.HISTORY_MIN_THRESHOLD_BYPASS:
                # Allow history-boosted results slightly below threshold
                results.append((bookmark, final_score))

        # Sort by final score (base capped at 80 + history up to 20)
        def sort_key(item):
            bookmark, final_score = item
            # Final score is already calculated as base_component + history_component
            return (-final_score, len(bookmark.name), bookmark.name.lower())

        results.sort(key=sort_key)

        # Limit results
        return results[:config.MAX_RESULTS]

    def _calculate_score(self, bookmark: Bookmark, keywords: List[str]) -> int:
        """Calculate relevance score for a bookmark with multi-keyword matching"""
        
        if not keywords:
            return 0
        
        # For multi-keyword search, all keywords must match
        name_scores = []
        folder_scores = []
        
        for keyword in keywords:
            name_score = self._score_text(bookmark.name, keyword)
            folder_score = self._score_text(bookmark.folder, keyword)
            
            # Each keyword must match at least one field
            max_score_for_keyword = max(name_score, folder_score)
            
            if max_score_for_keyword == 0:
                # If any keyword doesn't match, return 0
                return 0
            
            name_scores.append(name_score)
            folder_scores.append(folder_score)
        
        # Calculate weighted sum score
        # Name and folder have equal weight, but only count fields that matched
        avg_name_score = sum(name_scores) / len(name_scores)
        avg_folder_score = sum(folder_scores) / len(folder_scores)
        
        # Use the maximum of the two scores (prioritize best match)
        total_score = max(avg_name_score, avg_folder_score)
        
        # Bonus if both fields match
        if avg_name_score > 0 and avg_folder_score > 0:
            total_score = min(total_score + 5, 100)
        
        # Small bonus for matching all keywords in name
        if all(score > 0 for score in name_scores):
            total_score = total_score + 3
        
        # Additional small bonus: prefer matches at start of name
        if bookmark.name and keywords:
            name_lower = bookmark.name.lower()
            if name_lower.startswith(keywords[0].lower()):
                total_score = total_score + 2
        
        return int(min(total_score, 100))
    
    def _score_text(self, text: str, keyword: str) -> float:
        """Score how well a single keyword matches text (supports pinyin)"""
        if not text:
            return 0
        
        keyword = keyword.lower()
        text_lower = text.lower()
        
        # First try pinyin matching for Chinese text (higher priority)
        if self.pinyin_matcher.contains_chinese(text):
            pinyin_score = self.pinyin_matcher.score_match(text, keyword)
            if pinyin_score > 0:
                return float(pinyin_score)
        
        # For non-Chinese text
        import re
        
        # Exact match (complete text)
        if keyword == text_lower:
            return 100.0
        
        # Complete word match (keyword is a standalone word)
        word_pattern = r'\b' + re.escape(keyword) + r'\b'
        match = re.search(word_pattern, text_lower)
        if match:
            # Complete word at the start
            if text_lower.startswith(keyword + ' ') or text_lower.startswith(keyword + '-') or text_lower.startswith(keyword + '_'):
                return 98.0
            # Complete word (but text starts with this word, like "Edgeone" contains "edge")
            if text_lower.startswith(keyword):
                return 92.0
            # Complete word elsewhere
            return 95.0
        
        # Prefix match (text starts with keyword but keyword is not complete word)
        if text_lower.startswith(keyword):
            return 85.0
        
        # Word prefix match (any word starts with keyword)
        # Split by non-alphanumeric characters
        words = re.split(r'[^a-z0-9]+', text_lower)
        for i, word in enumerate(words):
            if word and word.startswith(keyword):
                # Earlier words get higher scores
                return 80.0 - (i * 2)
        
        # Substring match within a word (lower priority)
        # Only match if keyword is at least 2 characters to avoid too many false positives
        if len(keyword) >= 2 and keyword in text_lower:
            # Find if keyword is within a single word
            for i, word in enumerate(words):
                if word and keyword in word and not word.startswith(keyword):
                    # Keyword is inside a word, but check it's a meaningful match
                    # Avoid matching random character sequences
                    # Only match if it's near the beginning of the word
                    pos = word.find(keyword)
                    if pos <= 3:  # Within first 4 characters
                        return 65.0 - (i * 2) - (pos * 2)
        
        return 0
