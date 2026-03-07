"""
Unit tests for History Manager
"""
import sys
import os
import time
import tempfile
import shutil
from pathlib import Path

# Add parent src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock config before importing history_manager
import config
config.HISTORY_ENABLED = True
config.HISTORY_HALF_LIFE_DAYS = 30.0
config.HISTORY_SCORE_MAX = 20
config.HISTORY_MIN_THRESHOLD_BYPASS = 0.5
config.HISTORY_RETENTION_DAYS = 180

from history_manager import HistoryManager, HistoryRecord


class MockBookmark:
    """Mock bookmark for testing"""
    def __init__(self, name, url, folder=""):
        self.name = name
        self.url = url
        self.folder = folder


def create_temp_history_manager():
    """Create a HistoryManager with a temporary directory"""
    # Create a temp directory
    temp_dir = tempfile.mkdtemp()

    # Create manager
    manager = HistoryManager()

    # Save original path
    manager._original_data_dir = manager.data_dir
    manager._original_data_file = manager.data_file

    # Set temp paths
    manager.data_dir = Path(temp_dir)
    manager.data_file = manager.data_dir / 'history.json'
    manager.data = {"version": manager.DATA_VERSION, "records": {}}

    return manager, temp_dir


def cleanup_temp_history_manager(manager, temp_dir):
    """Clean up temporary history manager"""
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_history_record_creation():
    """Test HistoryRecord dataclass"""
    record = HistoryRecord(
        name="GitHub",
        folder="Development",
        frequency=5,
        last_used=1741420800,
        first_used=1740000000
    )

    assert record.name == "GitHub"
    assert record.folder == "Development"
    assert record.frequency == 5

    # Test serialization
    data = record.to_dict()
    assert data["name"] == "GitHub"

    # Test deserialization
    restored = HistoryRecord.from_dict(data)
    assert restored.name == record.name
    assert restored.frequency == record.frequency

    print("✓ HistoryRecord creation test passed")


def test_history_manager_basic():
    """Test basic HistoryManager operations"""
    manager, temp_dir = create_temp_history_manager()

    try:
        # Test recording selection
        bookmark = MockBookmark("GitHub", "https://github.com", "Development")
        manager.record_selection("github", bookmark)

        # Test retrieval
        record = manager.get_record("github", "https://github.com")
        assert record is not None
        assert record.name == "GitHub"
        assert record.frequency == 1

        # Test weight calculation
        weight = manager.get_weight("github", "https://github.com")
        assert 0 < weight <= 1.0

        # Record again to test frequency increment
        manager.record_selection("github", bookmark)
        record = manager.get_record("github", "https://github.com")
        assert record.frequency == 2

        print("✓ HistoryManager basic operations test passed")

    finally:
        cleanup_temp_history_manager(manager, temp_dir)


def test_weight_calculation():
    """Test weight calculation with frequency and time decay"""
    manager, temp_dir = create_temp_history_manager()

    try:
        now = int(time.time())

        # Create records with different frequencies and times
        high_freq_recent = HistoryRecord(
            name="Recent",
            folder="",
            frequency=20,
            last_used=now,
            first_used=now - 86400
        )

        low_freq_old = HistoryRecord(
            name="Old",
            folder="",
            frequency=1,
            last_used=now - 86400 * 60,  # 60 days ago
            first_used=now - 86400 * 90
        )

        # Calculate weights
        high_weight = manager._calculate_weight(high_freq_recent)
        low_weight = manager._calculate_weight(low_freq_old)

        # High frequency recent should have higher weight
        assert high_weight > low_weight

        # Weights should be in valid range
        assert 0 <= high_weight <= 1.0
        assert 0 <= low_weight <= 1.0

        # High frequency recent should be close to 1.0
        assert high_weight > 0.8

        print("✓ Weight calculation test passed")

    finally:
        cleanup_temp_history_manager(manager, temp_dir)


def test_time_decay():
    """Test time decay calculation"""
    manager, temp_dir = create_temp_history_manager()

    try:
        now = int(time.time())

        # Same frequency, different times
        recent = HistoryRecord("Test", "", 5, now, now - 86400)
        thirty_days = HistoryRecord("Test", "", 5, now - 86400 * 30, now - 86400 * 31)
        sixty_days = HistoryRecord("Test", "", 5, now - 86400 * 60, now - 86400 * 61)

        w1 = manager._calculate_weight(recent)
        w2 = manager._calculate_weight(thirty_days)
        w3 = manager._calculate_weight(sixty_days)

        # Should decrease over time
        assert w1 > w2 > w3

        # 30 days should be approximately half (with frequency factor)
        # Allow some tolerance due to frequency factor
        assert w2 < w1 * 0.8

        print("✓ Time decay test passed")

    finally:
        cleanup_temp_history_manager(manager, temp_dir)


def test_persistence():
    """Test data persistence across instances"""
    manager, temp_dir = create_temp_history_manager()

    try:
        # Create manager and add record
        bookmark = MockBookmark("Test", "https://test.com")
        manager.record_selection("test", bookmark)
        manager._save()  # Explicitly save

        # Create new manager pointing to same file
        manager2, temp_dir2 = create_temp_history_manager()
        manager2.data_dir = Path(temp_dir)
        manager2.data_file = manager2.data_dir / 'history.json'
        manager2._load()

        record = manager2.get_record("test", "https://test.com")

        assert record is not None
        assert record.name == "Test"
        assert record.frequency == 1

        cleanup_temp_history_manager(manager2, temp_dir2)

        print("✓ Persistence test passed")

    finally:
        cleanup_temp_history_manager(manager, temp_dir)


def test_query_case_insensitive():
    """Test query matching is case insensitive"""
    manager, temp_dir = create_temp_history_manager()

    try:
        bookmark = MockBookmark("GitHub", "https://github.com")

        # Record with lowercase
        manager.record_selection("github", bookmark)

        # Retrieve with uppercase
        record = manager.get_record("GITHUB", "https://github.com")
        assert record is not None

        # Weight should also work
        weight = manager.get_weight("Github", "https://github.com")
        assert weight > 0

        print("✓ Case insensitivity test passed")

    finally:
        cleanup_temp_history_manager(manager, temp_dir)


def test_stats():
    """Test statistics reporting"""
    manager, temp_dir = create_temp_history_manager()

    try:
        stats = manager.get_stats()
        assert stats["total_queries"] == 0
        assert stats["total_bookmarks"] == 0

        # Add some records
        manager.record_selection("query1", MockBookmark("B1", "https://b1.com"))
        manager.record_selection("query1", MockBookmark("B2", "https://b2.com"))
        manager.record_selection("query2", MockBookmark("B3", "https://b3.com"))

        stats = manager.get_stats()
        assert stats["total_queries"] == 2
        assert stats["total_bookmarks"] == 3

        print("✓ Stats test passed")

    finally:
        cleanup_temp_history_manager(manager, temp_dir)


def test_disabled_history():
    """Test behavior when history is disabled"""
    manager, temp_dir = create_temp_history_manager()

    try:
        # Disable history
        config.HISTORY_ENABLED = False

        bookmark = MockBookmark("Test", "https://test.com")

        # Should not record
        manager.record_selection("test", bookmark)

        # Should not find anything
        record = manager.get_record("test", "https://test.com")
        assert record is None

        # Re-enable for other tests
        config.HISTORY_ENABLED = True

        print("✓ Disabled history test passed")

    finally:
        cleanup_temp_history_manager(manager, temp_dir)


def run_all_tests():
    """Run all tests"""
    print("\n=== Running History Manager Tests ===\n")

    test_history_record_creation()
    test_history_manager_basic()
    test_weight_calculation()
    test_time_decay()
    test_persistence()
    test_query_case_insensitive()
    test_stats()
    test_disabled_history()

    print("\n=== All Tests Passed ===")


if __name__ == "__main__":
    run_all_tests()
