#!/usr/bin/env python3
"""
Test search engine with real bookmark data
"""
import sys
from bookmark_parser import BookmarkParser
from search_engine import SearchEngine
import config

def test_search(engine, bookmarks, query, expected_keywords=None, description=""):
    """Test a search query"""
    results = engine.search(bookmarks, query)

    print(f"\n查询: '{query}' {description}")
    print(f"结果数: {len(results)}")

    if results:
        print("前5个结果:")
        for i, (bookmark, score) in enumerate(results[:5], 1):
            folder_short = bookmark.folder.split('/')[-1] if bookmark.folder else ""
            print(f"  {i}. [{score:3d}分] [{folder_short}] {bookmark.name}")

        if expected_keywords:
            found = False
            for keyword in expected_keywords:
                if any(keyword.lower() in r[0].name.lower() or keyword.lower() in r[0].folder.lower() for r in results[:3]):
                    found = True
                    break

            if found:
                print(f"✓ 正确：前3个结果包含期望关键词 {expected_keywords}")
            else:
                print(f"✗ 错误：前3个结果不包含期望关键词 {expected_keywords}")
                return False
    else:
        print("  无结果")
        if expected_keywords:
            print(f"✗ 错误：期望找到包含 {expected_keywords} 的书签")
            return False

    return True

# Load real bookmarks
print("=" * 80)
print("使用真实书签数据测试搜索引擎")
print("=" * 80)

parser = BookmarkParser(config.DEFAULT_BOOKMARK_PATH)
bookmarks = parser.get_bookmarks()
print(f"\n已加载 {len(bookmarks)} 个书签\n")

engine = SearchEngine()

# Test cases based on real bookmarks
test_cases = []

passed = 0
failed = 0

for query, expected, desc in test_cases:
    if test_search(engine, bookmarks, query, expected, desc):
        passed += 1
    else:
        failed += 1

print("\n" + "=" * 80)
print(f"测试完成: {passed} 通过, {failed} 失败")
print("=" * 80)
