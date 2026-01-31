import logging
"""
Cache Yardımcı Fonksiyonlar
Performans artışı için basit cache mekanizması
"""
import hashlib
import json
import os
import time
from typing import Any, Optional


class SimpleCache:
    """Basit dosya tabanlı cache sistemi"""

    def __init__(self, cache_dir: str = 'data/cache', ttl: int = 3600):
        self.cache_dir = cache_dir
        self.ttl = ttl  # Saniye cinsinden yaşam süresi

        # Cache klasörünü oluştur
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_key(self, key: str) -> str:
        """Cache anahtarını hash'le"""
        return hashlib.sha256(key.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> str:
        """Cache dosya yolunu al"""
        cache_key = self._get_cache_key(key)
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, key: str) -> Optional[Any]:
        """Cache'den veri al"""
        try:
            cache_path = self._get_cache_path(key)

            if not os.path.exists(cache_path):
                return None

            # Dosyayı oku
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # TTL kontrolü
            if time.time() - cache_data['timestamp'] > self.ttl:
                # Süresi dolmuş, sil
                os.remove(cache_path)
                return None

            return cache_data['value']

        except Exception:
            return None

    def set(self, key: str, value: Any) -> bool:
        """Cache'e veri kaydet"""
        try:
            cache_path = self._get_cache_path(key)

            cache_data = {
                'timestamp': time.time(),
                'value': value
            }

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f)

            return True

        except Exception as e:
            logging.error(f"[CacheHelper] Set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Cache'den veri sil"""
        try:
            cache_path = self._get_cache_path(key)

            if os.path.exists(cache_path):
                os.remove(cache_path)

            return True

        except Exception:
            return False

    def clear(self) -> int:
        """Tüm cache'i temizle"""
        try:
            count = 0
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
                    count += 1

            return count

        except Exception as e:
            logging.error(f"[CacheHelper] Clear error: {e}")
            return 0

    def clear_expired(self) -> int:
        """Süresi dolmuş cache'leri temizle"""
        try:
            count = 0
            current_time = time.time()

            for file in os.listdir(self.cache_dir):
                if not file.endswith('.json'):
                    continue

                file_path = os.path.join(self.cache_dir, file)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)

                    if current_time - cache_data['timestamp'] > self.ttl:
                        os.remove(file_path)
                        count += 1
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

            return count

        except Exception:
            return 0

# Global cache instance
_cache = None

def get_cache() -> SimpleCache:
    """Global cache instance'ı al"""
    global _cache
    if _cache is None:
        _cache = SimpleCache()
    return _cache

# End of file


