"""
Basit cache mekanizması - Memory-based caching
Database sorguları ve hesaplamalar için kullanılır
"""

import logging
import hashlib
import json
import time
import threading
from functools import wraps
from typing import Any, Callable, Optional


class SimpleCache:
    """Basit memory cache"""

    def __init__(self, ttl: int = 300) -> None:
        """
        Args:
            ttl: Time to live (saniye) - Varsayılan 5 dakika
        """
        self.cache = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """Cache'den veri al"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                # Expired
                del self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Cache'e veri ekle"""
        self.cache[key] = (value, time.time())

    def delete(self, key: str) -> None:
        """Cache'den sil"""
        if key in self.cache:
            del self.cache[key]

    def clear(self) -> None:
        """Tüm cache'i temizle"""
        self.cache.clear()

    def get_size(self) -> int:
        """Cache boyutu"""
        return len(self.cache)

# Global cache instance
_global_cache = SimpleCache(ttl=300)  # 5 dakika

def cached(ttl: int = 300) -> None:
    """
    Decorator - Fonksiyon sonuçlarını cache'ler
    
    Kullanım:
        @cached(ttl=600)
        def expensive_function(param1, param2) -> None:
            # Pahalı işlem
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            # Cache key oluştur (fonksiyon adı + parametreler)
            key_data = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs
            }
            cache_key = hashlib.md5(
                json.dumps(key_data, sort_keys=True, default=str).encode()
            ).hexdigest()

            # Cache'den kontrol et
            cached_result = _global_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache'de yoksa hesapla
            result = func(*args, **kwargs)

            # Cache'e kaydet
            _global_cache.set(cache_key, result)

            return result
        return wrapper
    return decorator

def clear_cache() -> None:
    """Global cache'i temizle"""
    _global_cache.clear()

def get_cache_stats() -> None:
    """Cache istatistikleri"""
    return {
        'size': _global_cache.get_size(),
        'ttl': _global_cache.ttl
    }

# User permissions cache
class UserPermissionsCache:
    """Kullanıcı yetkileri için özel cache"""

    def __init__(self) -> None:
        self.cache = SimpleCache(ttl=600)  # 10 dakika

    def get_permissions(self, user_id: int) -> Optional[set]:
        """Kullanıcı yetkilerini cache'den al"""
        return self.cache.get(f"user_permissions_{user_id}")

    def set_permissions(self, user_id: int, permissions: set) -> None:
        """Kullanıcı yetkilerini cache'e ekle"""
        self.cache.set(f"user_permissions_{user_id}", permissions)

    def invalidate_user(self, user_id: int) -> None:
        """Kullanıcı cache'ini sil (yetki değiştiğinde)"""
        self.cache.delete(f"user_permissions_{user_id}")

    def clear(self) -> None:
        """Tüm user cache'i temizle"""
        self.cache.clear()

# Global user permissions cache
user_permissions_cache = UserPermissionsCache()

# Database query cache
class QueryCache:
    """Database sorguları için cache"""

    def __init__(self) -> None:
        self.cache = SimpleCache(ttl=180)  # 3 dakika

    def get_query_result(self, query: str, params: tuple = ()) -> Optional[Any]:
        """Sorgu sonucunu cache'den al"""
        key = hashlib.md5(f"{query}_{params}".encode()).hexdigest()
        return self.cache.get(key)

    def set_query_result(self, query: str, params: tuple, result: Any) -> None:
        """Sorgu sonucunu cache'e ekle"""
        key = hashlib.md5(f"{query}_{params}".encode()).hexdigest()
        self.cache.set(key, result)

    def clear(self) -> None:
        """Tüm query cache'i temizle"""
        self.cache.clear()

# Global query cache
query_cache = QueryCache()

# End of file


