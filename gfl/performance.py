"""Performance optimizations for GeneForgeLang.

This module provides:
1. Lazy loading for expensive operations
2. Intelligent caching with TTL and size limits
3. Memory-efficient AST processing
4. Plugin loading optimization
5. Performance monitoring and metrics
"""

from __future__ import annotations

import functools
import hashlib
import logging
import time
import weakref
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar
from threading import Lock, RLock
import pickle

logger = logging.getLogger(__name__)

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


@dataclass
class CacheStats:
    """Cache performance statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        return 1.0 - self.hit_rate

    def reset(self) -> None:
        """Reset all statistics."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0


@dataclass
class CacheEntry(Generic[V]):
    """Cache entry with metadata."""

    value: V
    created_at: float
    last_accessed: float
    access_count: int = 1
    size: int = 0

    def is_expired(self, ttl: Optional[float]) -> bool:
        """Check if entry has expired."""
        if ttl is None:
            return False
        return time.time() - self.created_at > ttl

    def touch(self) -> None:
        """Update access metadata."""
        self.last_accessed = time.time()
        self.access_count += 1


class CacheEvictionPolicy(ABC):
    """Abstract base class for cache eviction policies."""

    @abstractmethod
    def should_evict(self, entry: CacheEntry, **kwargs) -> bool:
        """Determine if an entry should be evicted."""
        pass

    @abstractmethod
    def select_victim(self, entries: Dict[Any, CacheEntry]) -> Any:
        """Select which entry to evict."""
        pass


class LRUEvictionPolicy(CacheEvictionPolicy):
    """Least Recently Used eviction policy."""

    def should_evict(self, entry: CacheEntry, **kwargs) -> bool:
        """Always evict when needed (LRU is about ordering)."""
        return True

    def select_victim(self, entries: Dict[Any, CacheEntry]) -> Any:
        """Select least recently used entry."""
        if not entries:
            return None
        return min(entries.keys(), key=lambda k: entries[k].last_accessed)


class TTLEvictionPolicy(CacheEvictionPolicy):
    """Time-to-Live eviction policy."""

    def __init__(self, ttl: float):
        self.ttl = ttl

    def should_evict(self, entry: CacheEntry, **kwargs) -> bool:
        """Evict if entry has expired."""
        return entry.is_expired(self.ttl)

    def select_victim(self, entries: Dict[Any, CacheEntry]) -> Any:
        """Select oldest expired entry."""
        expired = {k: v for k, v in entries.items() if self.should_evict(v)}
        if not expired:
            return None
        return min(expired.keys(), key=lambda k: expired[k].created_at)


class IntelligentCache(Generic[K, V]):
    """High-performance cache with multiple eviction policies and statistics."""

    def __init__(
        self,
        max_size: int = 1000,
        ttl: Optional[float] = None,
        eviction_policy: Optional[CacheEvictionPolicy] = None,
        enable_stats: bool = True,
        thread_safe: bool = True,
    ):
        self.max_size = max_size
        self.ttl = ttl
        self.enable_stats = enable_stats
        self._entries: Dict[K, CacheEntry[V]] = {}
        self._lock = RLock() if thread_safe else None
        self._stats = CacheStats() if enable_stats else None

        # Set up eviction policy
        if eviction_policy is None:
            if ttl is not None:
                self.eviction_policy = TTLEvictionPolicy(ttl)
            else:
                self.eviction_policy = LRUEvictionPolicy()
        else:
            self.eviction_policy = eviction_policy

    def _with_lock(self, func: Callable) -> Any:
        """Execute function with lock if thread safety is enabled."""
        if self._lock:
            with self._lock:
                return func()
        else:
            return func()

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Get value from cache."""

        def _get():
            entry = self._entries.get(key)

            if entry is None:
                if self._stats:
                    self._stats.misses += 1
                return default

            # Check if expired
            if entry.is_expired(self.ttl):
                del self._entries[key]
                if self._stats:
                    self._stats.misses += 1
                    self._stats.size -= 1
                return default

            # Update access metadata
            entry.touch()

            if self._stats:
                self._stats.hits += 1

            return entry.value

        return self._with_lock(_get)

    def put(self, key: K, value: V) -> None:
        """Put value in cache."""

        def _put():
            # Calculate approximate size
            size = self._estimate_size(value)

            # Create new entry
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                size=size,
            )

            # Check if we need to evict
            if len(self._entries) >= self.max_size and key not in self._entries:
                self._evict_entries(1)

            # Store entry
            old_entry = self._entries.get(key)
            self._entries[key] = entry

            # Update stats
            if self._stats:
                if old_entry is None:
                    self._stats.size += 1
                self._stats.max_size = max(self._stats.max_size, len(self._entries))

        self._with_lock(_put)

    def _evict_entries(self, count: int = 1) -> int:
        """Evict entries from cache."""
        evicted = 0

        for _ in range(count):
            # First try to evict expired entries
            expired_key = None
            for key, entry in self._entries.items():
                if entry.is_expired(self.ttl):
                    expired_key = key
                    break

            if expired_key:
                del self._entries[expired_key]
                evicted += 1
                if self._stats:
                    self._stats.evictions += 1
                    self._stats.size -= 1
                continue

            # Use eviction policy to select victim
            victim_key = self.eviction_policy.select_victim(self._entries)
            if victim_key is not None:
                del self._entries[victim_key]
                evicted += 1
                if self._stats:
                    self._stats.evictions += 1
                    self._stats.size -= 1
            else:
                break

        return evicted

    def _estimate_size(self, value: V) -> int:
        """Estimate memory size of value."""
        try:
            # Quick size estimation - not perfect but fast
            if hasattr(value, "__sizeof__"):
                return value.__sizeof__()
            elif isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (list, tuple, set)):
                return len(value) * 8  # Rough estimate
            elif isinstance(value, dict):
                return len(value) * 16  # Rough estimate for key-value pairs
            else:
                return 64  # Default estimate
        except Exception:
            return 64

    def clear(self) -> None:
        """Clear all cache entries."""

        def _clear():
            self._entries.clear()
            if self._stats:
                self._stats.size = 0

        self._with_lock(_clear)

    def size(self) -> int:
        """Get current cache size."""
        return len(self._entries)

    def stats(self) -> Optional[CacheStats]:
        """Get cache statistics."""
        return self._stats

    def cleanup(self) -> int:
        """Remove expired entries and return count removed."""

        def _cleanup():
            expired_keys = [
                key
                for key, entry in self._entries.items()
                if entry.is_expired(self.ttl)
            ]

            for key in expired_keys:
                del self._entries[key]
                if self._stats:
                    self._stats.size -= 1

            return len(expired_keys)

        return self._with_lock(_cleanup)


class LazyLoader(Generic[T]):
    """Lazy loader for expensive operations with caching."""

    def __init__(self, loader_func: Callable[[], T], cache_key: Optional[str] = None):
        self._loader_func = loader_func
        self._cache_key = cache_key or f"lazy_{id(self)}"
        self._loaded = False
        self._value: Optional[T] = None
        self._error: Optional[Exception] = None
        self._lock = Lock()

    def get(self) -> T:
        """Get the loaded value, loading if necessary."""
        if self._loaded and self._error is None:
            return self._value

        with self._lock:
            if self._loaded:
                if self._error:
                    raise self._error
                return self._value

            try:
                logger.debug(f"Lazy loading: {self._cache_key}")
                self._value = self._loader_func()
                self._loaded = True
                self._error = None
                return self._value
            except Exception as e:
                self._error = e
                self._loaded = True  # Mark as loaded even on error
                logger.error(f"Lazy loading failed for {self._cache_key}: {e}")
                raise

    def is_loaded(self) -> bool:
        """Check if value has been loaded."""
        return self._loaded

    def reset(self) -> None:
        """Reset loader state."""
        with self._lock:
            self._loaded = False
            self._value = None
            self._error = None


class PerformanceOptimizer:
    """Central performance optimization coordinator."""

    def __init__(self):
        self._caches: Dict[str, IntelligentCache] = {}
        self._lazy_loaders: weakref.WeakSet = weakref.WeakSet()
        self._enabled = True

        # Default caches
        self._setup_default_caches()

    def _setup_default_caches(self) -> None:
        """Set up default caches for common operations."""
        # AST parsing cache
        self.register_cache(
            "ast_parse",
            IntelligentCache(max_size=100, ttl=300.0),  # 5 minute TTL
        )

        # Schema validation cache
        self.register_cache(
            "schema_validation",
            IntelligentCache(max_size=500, ttl=600.0),  # 10 minute TTL
        )

        # Plugin discovery cache
        self.register_cache(
            "plugin_discovery",
            IntelligentCache(max_size=50, ttl=1800.0),  # 30 minute TTL
        )

        # File content cache
        self.register_cache(
            "file_content",
            IntelligentCache(max_size=200, ttl=300.0),  # 5 minute TTL
        )

    def register_cache(self, name: str, cache: IntelligentCache) -> None:
        """Register a named cache."""
        self._caches[name] = cache

    def get_cache(self, name: str) -> Optional[IntelligentCache]:
        """Get a registered cache."""
        return self._caches.get(name)

    def create_lazy_loader(
        self, loader_func: Callable[[], T], cache_key: Optional[str] = None
    ) -> LazyLoader[T]:
        """Create a lazy loader."""
        loader = LazyLoader(loader_func, cache_key)
        self._lazy_loaders.add(loader)
        return loader

    def clear_all_caches(self) -> None:
        """Clear all registered caches."""
        for cache in self._caches.values():
            cache.clear()

    def cleanup_all_caches(self) -> Dict[str, int]:
        """Clean up expired entries in all caches."""
        results = {}
        for name, cache in self._caches.items():
            removed = cache.cleanup()
            results[name] = removed
        return results

    def get_cache_stats(self) -> Dict[str, Optional[CacheStats]]:
        """Get statistics for all caches."""
        return {name: cache.stats() for name, cache in self._caches.items()}

    def enable(self) -> None:
        """Enable performance optimizations."""
        self._enabled = True

    def disable(self) -> None:
        """Disable performance optimizations."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if optimizations are enabled."""
        return self._enabled


# Global performance optimizer instance
_optimizer = PerformanceOptimizer()


def get_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer."""
    return _optimizer


def cached(
    cache_name: str = "default", ttl: Optional[float] = None, max_size: int = 1000
):
    """Decorator for caching function results."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Create cache if it doesn't exist
        cache = _optimizer.get_cache(cache_name)
        if cache is None:
            cache = IntelligentCache(max_size=max_size, ttl=ttl)
            _optimizer.register_cache(cache_name, cache)

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if not _optimizer.is_enabled():
                return func(*args, **kwargs)

            # Create cache key from arguments
            key = _create_cache_key(func.__name__, args, kwargs)

            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result

            # Compute and cache result
            result = func(*args, **kwargs)
            cache.put(key, result)

            return result

        # Add cache management methods
        wrapper._cache = cache
        wrapper.clear_cache = lambda: cache.clear()
        wrapper.cache_stats = lambda: cache.stats()

        return wrapper

    return decorator


def _create_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Create a cache key from function arguments."""
    try:
        # Create a hashable representation
        key_data = (func_name, args, tuple(sorted(kwargs.items())))
        key_str = pickle.dumps(key_data)
        return hashlib.sha256(key_str).hexdigest()
    except (TypeError, pickle.PicklingError):
        # Fallback for non-pickleable arguments
        return f"{func_name}_{hash((str(args), str(kwargs)))}"


def lazy_property(func: Callable[[Any], T]) -> property:
    """Decorator for lazy property evaluation."""
    attr_name = f"_lazy_{func.__name__}"

    @functools.wraps(func)
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)

    return property(wrapper)


class PerformanceMonitor:
    """Monitor performance metrics for GFL operations."""

    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self._enabled = True

    def time_operation(self, operation_name: str):
        """Context manager for timing operations."""
        return _TimingContext(self, operation_name)

    def record_metric(self, name: str, value: float) -> None:
        """Record a performance metric."""
        if not self._enabled:
            return

        if name not in self._metrics:
            self._metrics[name] = []

        self._metrics[name].append(value)

        # Keep only recent measurements (last 1000)
        if len(self._metrics[name]) > 1000:
            self._metrics[name] = self._metrics[name][-1000:]

    def get_stats(self, operation_name: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        if operation_name not in self._metrics:
            return {}

        values = self._metrics[operation_name]
        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "total": sum(values),
        }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all operations."""
        return {name: self.get_stats(name) for name in self._metrics.keys()}

    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        self._metrics.clear()

    def enable(self) -> None:
        """Enable performance monitoring."""
        self._enabled = True

    def disable(self) -> None:
        """Disable performance monitoring."""
        self._enabled = False


class _TimingContext:
    """Context manager for timing operations."""

    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.perf_counter() - self.start_time
            self.monitor.record_metric(self.operation_name, duration)


# Global performance monitor
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    return _monitor


# Export commonly used functions and classes
__all__ = [
    "IntelligentCache",
    "LazyLoader",
    "PerformanceOptimizer",
    "PerformanceMonitor",
    "CacheStats",
    "get_optimizer",
    "get_monitor",
    "cached",
    "lazy_property",
]
