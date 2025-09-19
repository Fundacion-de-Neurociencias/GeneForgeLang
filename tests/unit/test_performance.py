"""Tests for performance optimization module."""

import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from gfl.performance import (
    IntelligentCache,
    LazyLoader,
    LRUEvictionPolicy,
    PerformanceMonitor,
    PerformanceOptimizer,
    cached,
    get_monitor,
    get_optimizer,
    lazy_property,
)


class TestIntelligentCache:
    """Test intelligent cache functionality."""

    def test_basic_cache_operations(self):
        """Test basic cache put/get operations."""
        cache = IntelligentCache[str, int](max_size=3)

        # Test put and get
        cache.put("key1", 100)
        assert cache.get("key1") == 100

        # Test default value
        assert cache.get("nonexistent", 42) == 42
        assert cache.get("nonexistent") is None

        # Test size
        assert cache.size() == 1

    def test_lru_eviction(self):
        """Test LRU eviction policy."""
        cache = IntelligentCache[str, int](max_size=2, eviction_policy=LRUEvictionPolicy())

        cache.put("key1", 100)
        cache.put("key2", 200)

        # Access key1 to make it recently used
        cache.get("key1")

        # Add key3, should evict key2 (least recently used)
        cache.put("key3", 300)

        assert cache.get("key1") == 100
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == 300

    def test_ttl_eviction(self):
        """Test TTL-based eviction."""
        cache = IntelligentCache[str, int](max_size=10, ttl=0.1)  # 100ms TTL

        cache.put("key1", 100)
        assert cache.get("key1") == 100

        # Wait for expiration
        time.sleep(0.15)

        # Should be expired now
        assert cache.get("key1") is None

    def test_cache_stats(self):
        """Test cache statistics tracking."""
        cache = IntelligentCache[str, int](max_size=3, enable_stats=True)

        stats = cache.stats()
        assert stats is not None
        assert stats.hits == 0
        assert stats.misses == 0

        # Test hit
        cache.put("key1", 100)
        cache.get("key1")
        stats = cache.stats()
        assert stats.hits == 1
        assert stats.misses == 0

        # Test miss
        cache.get("nonexistent")
        stats = cache.stats()
        assert stats.hits == 1
        assert stats.misses == 1

        assert stats.hit_rate == 0.5
        assert stats.miss_rate == 0.5

    def test_thread_safety(self):
        """Test thread-safe cache operations."""
        cache = IntelligentCache[str, int](max_size=100, thread_safe=True)

        def worker(thread_id: int):
            for i in range(50):
                key = f"thread_{thread_id}_key_{i}"
                cache.put(key, i)
                assert cache.get(key) == i

        # Run multiple threads concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, i) for i in range(5)]
            for future in futures:
                future.result()  # Wait for completion

        # Should have entries from all threads
        assert cache.size() > 0

    def test_cache_cleanup(self):
        """Test cache cleanup of expired entries."""
        cache = IntelligentCache[str, int](max_size=10, ttl=0.1)

        # Add some entries
        for i in range(5):
            cache.put(f"key_{i}", i)

        assert cache.size() == 5

        # Wait for expiration
        time.sleep(0.15)

        # Cleanup should remove expired entries
        removed = cache.cleanup()
        assert removed == 5
        assert cache.size() == 0


class TestLazyLoader:
    """Test lazy loading functionality."""

    def test_basic_lazy_loading(self):
        """Test basic lazy loading behavior."""
        call_count = 0

        def expensive_operation():
            nonlocal call_count
            call_count += 1
            return "expensive_result"

        loader = LazyLoader(expensive_operation)

        # Should not be loaded initially
        assert not loader.is_loaded()

        # First access should call the function
        result1 = loader.get()
        assert result1 == "expensive_result"
        assert call_count == 1
        assert loader.is_loaded()

        # Second access should not call the function again
        result2 = loader.get()
        assert result2 == "expensive_result"
        assert call_count == 1  # Not incremented

    def test_lazy_loader_error_handling(self):
        """Test lazy loader error handling."""

        def failing_operation():
            raise ValueError("Operation failed")

        loader = LazyLoader(failing_operation)

        # First access should raise the exception
        with pytest.raises(ValueError, match="Operation failed"):
            loader.get()

        # Should be marked as loaded even with error
        assert loader.is_loaded()

        # Second access should raise the same exception
        with pytest.raises(ValueError, match="Operation failed"):
            loader.get()

    def test_lazy_loader_reset(self):
        """Test lazy loader reset functionality."""
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"

        loader = LazyLoader(operation)

        # First load
        result1 = loader.get()
        assert result1 == "result_1"
        assert call_count == 1

        # Reset and load again
        loader.reset()
        assert not loader.is_loaded()

        result2 = loader.get()
        assert result2 == "result_2"
        assert call_count == 2


class TestCachedDecorator:
    """Test the @cached decorator."""

    def test_cached_function(self):
        """Test function caching with decorator."""
        call_count = 0

        @cached(cache_name="test_cache", max_size=10, ttl=60.0)
        def expensive_function(x: int, y: int = 10) -> int:
            nonlocal call_count
            call_count += 1
            return x + y

        # First call should execute function
        result1 = expensive_function(5, 15)
        assert result1 == 20
        assert call_count == 1

        # Second call with same args should use cache
        result2 = expensive_function(5, 15)
        assert result2 == 20
        assert call_count == 1  # Not incremented

        # Different args should execute function
        result3 = expensive_function(10, 15)
        assert result3 == 25
        assert call_count == 2

    def test_cached_function_with_optimizer_disabled(self):
        """Test cached function when optimizer is disabled."""
        optimizer = get_optimizer()

        call_count = 0

        @cached(cache_name="disabled_test", max_size=10)
        def test_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # Disable optimizer
        optimizer.disable()

        try:
            # Both calls should execute function
            result1 = test_function(5)
            result2 = test_function(5)

            assert result1 == 10
            assert result2 == 10
            assert call_count == 2  # Both calls executed

        finally:
            # Re-enable optimizer
            optimizer.enable()

    def test_lazy_property_decorator(self):
        """Test lazy property decorator."""

        class TestClass:
            def __init__(self):
                self.compute_count = 0

            @lazy_property
            def expensive_property(self):
                self.compute_count += 1
                return "computed_value"

        obj = TestClass()

        # First access should compute
        value1 = obj.expensive_property
        assert value1 == "computed_value"
        assert obj.compute_count == 1

        # Second access should not recompute
        value2 = obj.expensive_property
        assert value2 == "computed_value"
        assert obj.compute_count == 1  # Not incremented


class TestPerformanceMonitor:
    """Test performance monitoring functionality."""

    def test_basic_monitoring(self):
        """Test basic performance monitoring."""
        monitor = PerformanceMonitor()

        # Test timing context
        with monitor.time_operation("test_op"):
            time.sleep(0.01)  # 10ms

        stats = monitor.get_stats("test_op")
        assert stats["count"] == 1
        assert stats["min"] >= 0.009  # Should be at least 9ms
        assert stats["max"] >= 0.009
        assert stats["avg"] >= 0.009

    def test_multiple_operations(self):
        """Test monitoring multiple operations."""
        monitor = PerformanceMonitor()

        # Record multiple operations
        for i in range(3):
            with monitor.time_operation("batch_op"):
                time.sleep(0.001)  # 1ms each

        stats = monitor.get_stats("batch_op")
        assert stats["count"] == 3
        assert stats["total"] >= 0.003  # At least 3ms total

    def test_monitor_disabled(self):
        """Test monitoring when disabled."""
        monitor = PerformanceMonitor()
        monitor.disable()

        with monitor.time_operation("disabled_op"):
            time.sleep(0.01)

        # Should not record anything when disabled
        stats = monitor.get_stats("disabled_op")
        assert stats == {}

        monitor.enable()

    def test_global_monitor(self):
        """Test global monitor instance."""
        monitor = get_monitor()

        with monitor.time_operation("global_test"):
            time.sleep(0.001)

        stats = monitor.get_stats("global_test")
        assert stats["count"] >= 1


class TestPerformanceOptimizer:
    """Test performance optimizer coordination."""

    def test_optimizer_cache_management(self):
        """Test optimizer cache management."""
        optimizer = PerformanceOptimizer()

        # Create and register a cache
        cache = IntelligentCache[str, int](max_size=10)
        optimizer.register_cache("test_cache", cache)

        # Verify cache is registered
        retrieved_cache = optimizer.get_cache("test_cache")
        assert retrieved_cache is cache

        # Test cache operations through optimizer
        cache.put("key", 123)
        assert cache.get("key") == 123

        # Test clear all caches
        optimizer.clear_all_caches()
        assert cache.get("key") is None

    def test_cache_cleanup(self):
        """Test cache cleanup functionality."""
        optimizer = PerformanceOptimizer()

        # Create cache with TTL
        cache = IntelligentCache[str, int](max_size=10, ttl=0.1)
        optimizer.register_cache("ttl_cache", cache)

        # Add some entries
        cache.put("key1", 100)
        cache.put("key2", 200)

        # Wait for expiration
        time.sleep(0.15)

        # Cleanup should remove expired entries
        cleanup_results = optimizer.cleanup_all_caches()
        assert cleanup_results["ttl_cache"] == 2

    def test_cache_stats_collection(self):
        """Test cache statistics collection."""
        optimizer = PerformanceOptimizer()

        # Create cache and perform operations
        cache = IntelligentCache[str, int](max_size=10, enable_stats=True)
        optimizer.register_cache("stats_cache", cache)

        cache.put("key", 123)
        cache.get("key")  # Hit
        cache.get("missing")  # Miss

        # Get stats through optimizer
        all_stats = optimizer.get_cache_stats()
        stats = all_stats["stats_cache"]

        assert stats is not None
        assert stats.hits == 1
        assert stats.misses == 1

    def test_lazy_loader_creation(self):
        """Test lazy loader creation through optimizer."""
        optimizer = PerformanceOptimizer()

        def load_data():
            return "loaded_data"

        loader = optimizer.create_lazy_loader(load_data, "test_loader")

        assert not loader.is_loaded()
        result = loader.get()
        assert result == "loaded_data"
        assert loader.is_loaded()


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_api_performance_integration(self):
        """Test performance integration with API functions."""
        from gfl.api import parse, validate

        # Clear any existing performance data
        get_monitor().clear_metrics()

        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: TP53
        """

        # Parse multiple times (should benefit from caching)
        for _ in range(3):
            ast = parse(gfl_text)
            validate(ast)

        # Check that operations were monitored
        stats = get_monitor().get_all_stats()

        # Should have recorded timing for API operations
        assert "api_parse" in stats
        assert stats["api_parse"]["count"] == 3

    def test_concurrent_cache_access(self):
        """Test concurrent access to cached functions."""
        call_count = 0

        @cached(cache_name="concurrent_test", max_size=50)
        def compute_value(x: int) -> int:
            nonlocal call_count
            call_count += 1
            time.sleep(0.001)  # Simulate work
            return x * x

        def worker(thread_id: int):
            results = []
            for i in range(10):
                # Multiple threads computing same values
                result = compute_value(i % 5)  # Only 5 unique values
                results.append(result)
            return results

        # Run multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, i) for i in range(5)]
            results = [future.result() for future in futures]

        # Should have computed each unique value only once due to caching
        # call_count should be 5 (not 50) if caching works properly
        assert call_count <= 10  # Allow some cache misses due to timing

        # All results should be correct
        expected_results = [i * i for i in range(5)] * 2
        for thread_results in results:
            assert thread_results == expected_results

    def test_memory_efficiency(self):
        """Test memory efficiency of caching system."""
        # Create cache with size limit
        cache = IntelligentCache[str, str](max_size=5, enable_stats=True)

        # Add more items than the cache can hold
        for i in range(10):
            cache.put(f"key_{i}", f"value_{i}" * 100)  # Large values

        # Cache should not exceed max size
        assert cache.size() <= 5

        # Should have recorded evictions
        stats = cache.stats()
        assert stats.evictions > 0
        assert stats.size <= 5
