#!/usr/bin/env python3
"""
Quick test script for Edge Bookmarks functionality
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bookmark_parser import BookmarkParser
from search_engine import SearchEngine
import config

def test_bookmark_parsing():
    """Test bookmark parsing"""
    print("=" * 60)
    print("Testing Bookmark Parser")
    print("=" * 60)
    
    parser = BookmarkParser(config.DEFAULT_BOOKMARK_PATH)
    
    try:
        bookmarks = parser.parse()
        print(f"✓ Successfully parsed {len(bookmarks)} bookmarks")
        
        if bookmarks:
            print("\nSample bookmarks:")
            for i, bm in enumerate(bookmarks[:5]):
                print(f"  {i+1}. {bm.name}")
                print(f"     URL: {bm.url}")
                print(f"     Folder: {bm.folder}")
                print()
        
        return bookmarks
    except FileNotFoundError:
        print(f"✗ Error: Bookmark file not found")
        print(f"  Expected: {config.DEFAULT_BOOKMARK_PATH}")
        print(f"\n  Please update config.py with correct path")
        return []
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def test_search(bookmarks):
    """Test search functionality"""
    print("=" * 60)
    print("Testing Search Engine")
    print("=" * 60)
    
    if not bookmarks:
        print("✗ No bookmarks to search")
        return
    
    engine = SearchEngine()
    
    # Test queries
    test_queries = [
        "github",
        "google",
        "中国",
        "zg",  # pinyin initials
        "python"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = engine.search(bookmarks, query)
        
        if results:
            print(f"  Found {len(results)} results:")
            for i, (bm, score) in enumerate(results[:3]):
                print(f"    {i+1}. [{score}] {bm.name}")
        else:
            print(f"  No results found")

def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("Edge Bookmarks Plugin Test")
    print("=" * 60)
    print(f"Bookmark path: {config.DEFAULT_BOOKMARK_PATH}")
    print(f"Trigger keyword: {config.TRIGGER_KEYWORD}")
    print()
    
    # Test parsing
    bookmarks = test_bookmark_parsing()
    
    if bookmarks:
        # Test search
        test_search(bookmarks)
        
        print("\n" + "=" * 60)
        print("✓ All tests completed")
        print("=" * 60)
        print("\nTo install the plugin, run:")
        print("  ./install.sh")
        print("\nThen open KRunner (Alt+Space) and type:")
        print(f"  {config.TRIGGER_KEYWORD} <search query>")
    else:
        print("\n" + "=" * 60)
        print("✗ Tests failed - check bookmark path")
        print("=" * 60)

if __name__ == '__main__':
    main()
