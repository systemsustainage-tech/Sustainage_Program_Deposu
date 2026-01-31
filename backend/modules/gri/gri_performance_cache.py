#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Performance Optimization & Cache - Sprint 4
Performans optimizasyonu ve cache sistemi
"""

import logging
import hashlib
import os
import sqlite3
import threading
import time
from functools import wraps
from typing import Any, Dict, List, Optional
from config.database import DB_PATH


class GRIPerformanceCache:
    """GRI performans cache sistemi"""

    def __init__(self, db_path: str = DB_PATH, cache_duration: int = 3600) -> None:
        # db_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.cache_duration = cache_duration  # saniye
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.query_stats = {}
        self.performance_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_query_time': 0.0,
            'avg_query_time': 0.0
        }

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def generate_cache_key(self, query: str, params: tuple = ()) -> str:
        """Cache key oluştur"""
        key_string = f"{query}:{str(params)}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def is_cache_valid(self, cache_entry: Dict) -> bool:
        """Cache geçerliliğini kontrol et"""
        if not cache_entry:
            return False

        created_time = cache_entry.get('created_at', 0)
        return time.time() - created_time < self.cache_duration

    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Cache'den sonuç al"""
        with self.cache_lock:
            if cache_key in self.cache and self.is_cache_valid(self.cache[cache_key]):
                self.performance_stats['cache_hits'] += 1
                return self.cache[cache_key]['data']
            else:
                self.performance_stats['cache_misses'] += 1
                if cache_key in self.cache:
                    del self.cache[cache_key]
                return None

    def set_cached_result(self, cache_key: str, data: Any) -> None:
        """Cache'e sonuç kaydet"""
        with self.cache_lock:
            self.cache[cache_key] = {
                'data': data,
                'created_at': time.time()
            }

    def cached_query(self, query: str, params: tuple = (), fetch_all: bool = True) -> None:
        """Cache'li sorgu decorator"""
        def decorator(func) -> None:
            @wraps(func)
            def wrapper(*args, **kwargs) -> None:
                cache_key = self.generate_cache_key(query, params)

                # Cache'den kontrol et
                cached_result = self.get_cached_result(cache_key)
                if cached_result is not None:
                    return cached_result

                # Cache miss - veritabanından al
                start_time = time.time()
                result = func(*args, **kwargs)
                query_time = time.time() - start_time

                # Performans istatistiklerini güncelle
                self.performance_stats['total_queries'] += 1
                self.performance_stats['total_query_time'] += query_time
                self.performance_stats['avg_query_time'] = (
                    self.performance_stats['total_query_time'] /
                    self.performance_stats['total_queries']
                )

                # Cache'e kaydet
                self.set_cached_result(cache_key, result)

                return result

            return wrapper
        return decorator

    def get_gri_standards_cached(self, category: str = None) -> List[Dict]:
        """Cache'li GRI standartları getir"""
        query = "SELECT id, code, title, category, type, description FROM gri_standards"
        params = ()

        if category:
            query += " WHERE category = ?"
            params = (category,)

        query += " ORDER BY category, code"

        @self.cached_query(query, params)
        def _execute_query() -> None:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                return results
            finally:
                conn.close()

        return _execute_query()

    def get_gri_indicators_cached(self, standard_id: int = None, category: str = None) -> List[Dict]:
        """Cache'li GRI göstergeleri getir"""
        query = """
            SELECT 
                gi.id, gi.code, gi.title, gi.description, gi.unit, gi.methodology,
                gi.reporting_requirement, gi.priority, gi.requirement_level,
                gi.reporting_frequency, gi.data_quality, gi.audit_required,
                gi.validation_required, gi.digitalization_status, gi.cost_level,
                gi.time_requirement, gi.expertise_requirement, gi.sustainability_impact,
                gi.legal_compliance, gi.sector_specific, gi.international_standard,
                gi.metric_type, gi.scale_unit, gi.data_source_system, gi.reporting_format,
                gi.tsrs_esrs_mapping, gi.un_sdg_mapping, gi.gri_3_3_reference,
                gi.impact_area, gi.stakeholder_group,
                gs.code as standard_code, gs.title as standard_title, gs.category
            FROM gri_indicators gi
            JOIN gri_standards gs ON gi.standard_id = gs.id
        """

        conditions = []
        params = []

        if standard_id:
            conditions.append("gi.standard_id = ?")
            params.append(standard_id)

        if category:
            conditions.append("gs.category = ?")
            params.append(category)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY gs.category, gs.code, gi.code"

        @self.cached_query(query, tuple(params))
        def _execute_query() -> None:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                return results
            finally:
                conn.close()

        return _execute_query()

    def get_gri_responses_cached(self, company_id: int = 1, indicator_id: int = None) -> List[Dict]:
        """Cache'li GRI yanıtları getir"""
        query = """
            SELECT 
                gr.id, gr.company_id, gr.indicator_id, gr.period,
                gr.response_value, gr.numerical_value, gr.unit, gr.methodology,
                gr.reporting_status, gr.evidence_url, gr.notes, gr.created_at, gr.updated_at,
                gi.code as disclosure_code, gi.title as disclosure_title,
                gs.code as standard_code, gs.category
            FROM gri_responses gr
            JOIN gri_indicators gi ON gr.indicator_id = gi.id
            JOIN gri_standards gs ON gi.standard_id = gs.id
            WHERE gr.company_id = ?
        """

        params = [company_id]

        if indicator_id:
            query += " AND gr.indicator_id = ?"
            params.append(indicator_id)

        query += " ORDER BY gs.category, gi.code, gr.period"

        @self.cached_query(query, tuple(params))
        def _execute_query() -> None:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                return results
            finally:
                conn.close()

        return _execute_query()

    def get_gri_kpis_cached(self, indicator_id: int = None) -> List[Dict]:
        """Cache'li GRI KPI'ları getir"""
        query = """
            SELECT 
                k.id, k.indicator_id, k.name, k.formula, k.unit, k.frequency,
                k.owner, k.notes, k.created_at,
                gi.code as disclosure_code, gi.title as disclosure_title,
                gs.code as standard_code, gs.category
            FROM gri_kpis k
            JOIN gri_indicators gi ON k.indicator_id = gi.id
            JOIN gri_standards gs ON gi.standard_id = gs.id
        """

        params = []

        if indicator_id:
            query += " WHERE k.indicator_id = ?"
            params.append(indicator_id)

        query += " ORDER BY gs.category, gi.code, k.name"

        @self.cached_query(query, tuple(params))
        def _execute_query() -> None:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                return results
            finally:
                conn.close()

        return _execute_query()

    def get_gri_targets_cached(self, year: int = None) -> List[Dict]:
        """Cache'li GRI hedefleri getir"""
        query = """
            SELECT 
                t.id, t.indicator_id, t.year, t.target_value, t.unit, t.method,
                t.notes, t.created_at,
                gi.code as disclosure_code, gi.title as disclosure_title,
                gs.code as standard_code, gs.category
            FROM gri_targets t
            JOIN gri_indicators gi ON t.indicator_id = gi.id
            JOIN gri_standards gs ON gi.standard_id = gs.id
        """

        params = []

        if year:
            query += " WHERE t.year = ?"
            params.append(year)

        query += " ORDER BY t.year, gs.category, gi.code"

        @self.cached_query(query, tuple(params))
        def _execute_query() -> None:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                return results
            finally:
                conn.close()

        return _execute_query()

    def get_gri_risks_cached(self, risk_level: str = None) -> List[Dict]:
        """Cache'li GRI riskleri getir"""
        query = """
            SELECT 
                r.id, r.indicator_id, r.risk_level, r.impact, r.likelihood,
                r.notes, r.created_at,
                gi.code as disclosure_code, gi.title as disclosure_title,
                gs.code as standard_code, gs.category
            FROM gri_risks r
            JOIN gri_indicators gi ON r.indicator_id = gi.id
            JOIN gri_standards gs ON gi.standard_id = gs.id
        """

        params = []

        if risk_level:
            query += " WHERE r.risk_level = ?"
            params.append(risk_level)

        query += " ORDER BY r.risk_level, gs.category, gi.code"

        @self.cached_query(query, tuple(params))
        def _execute_query() -> None:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                return results
            finally:
                conn.close()

        return _execute_query()

    def get_mapping_summaries_cached(self) -> Dict:
        """Cache'li eşleştirme özetleri getir"""
        query = "mapping_summaries"

        @self.cached_query(query, ())
        def _execute_query() -> None:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                # SDG-GRI eşleştirme sayısı
                cursor.execute("SELECT COUNT(*) FROM map_sdg_gri")
                sdg_gri_count = cursor.fetchone()[0]

                # GRI-TSRS eşleştirme sayısı
                cursor.execute("SELECT COUNT(*) FROM map_gri_tsrs")
                gri_tsrs_count = cursor.fetchone()[0]

                # Kategori bazında dağılım
                cursor.execute("""
                    SELECT gs.category, COUNT(*) 
                    FROM gri_indicators gi
                    JOIN gri_standards gs ON gi.standard_id = gs.id
                    GROUP BY gs.category
                """)
                category_distribution = dict(cursor.fetchall())

                return {
                    'sdg_gri_mappings': sdg_gri_count,
                    'gri_tsrs_mappings': gri_tsrs_count,
                    'category_distribution': category_distribution
                }
            finally:
                conn.close()

        return _execute_query()

    def clear_cache(self) -> None:
        """Cache'i temizle"""
        with self.cache_lock:
            self.cache.clear()
            logging.info("GRI Cache temizlendi.")

    def clear_expired_cache(self) -> int:
        """Süresi dolmuş cache'leri temizle"""
        with self.cache_lock:
            expired_keys = []
            time.time()

            for key, entry in self.cache.items():
                if not self.is_cache_valid(entry):
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]

            if expired_keys:
                logging.info(f"{len(expired_keys)} süresi dolmuş cache kaydı temizlendi.")

            return len(expired_keys)

    def get_cache_stats(self) -> Dict:
        """Cache istatistiklerini getir"""
        with self.cache_lock:
            cache_size = len(self.cache)
            valid_entries = sum(1 for entry in self.cache.values() if self.is_cache_valid(entry))
            expired_entries = cache_size - valid_entries

            return {
                'cache_size': cache_size,
                'valid_entries': valid_entries,
                'expired_entries': expired_entries,
                'cache_hit_rate': (
                    self.performance_stats['cache_hits'] /
                    (self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']) * 100
                ) if (self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']) > 0 else 0,
                'performance_stats': self.performance_stats.copy()
            }

    def optimize_database(self) -> Dict:
        """Veritabanı optimizasyonu"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("GRI veritabanı optimizasyonu başlıyor...")

            # ANALYZE komutu - istatistikleri güncelle
            cursor.execute("ANALYZE")

            # VACUUM komutu - veritabanını optimize et
            cursor.execute("VACUUM")

            # Index'leri kontrol et
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND sql IS NOT NULL
                ORDER BY name
            """)
            indexes = cursor.fetchall()

            # Tablo boyutlarını kontrol et
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE 'gri_%'
                ORDER BY name
            """)
            table_names = cursor.fetchall()

            table_stats = []
            for table_name in table_names:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name[0]}")
                    count = cursor.fetchone()[0]
                    table_stats.append((table_name[0], count))
                except Exception:
                    table_stats.append((table_name[0], 0))

            conn.commit()

            optimization_result = {
                'analyze_completed': True,
                'vacuum_completed': True,
                'indexes': [idx[0] for idx in indexes],
                'table_stats': {table[0]: table[1] for table in table_stats}
            }

            logging.info("GRI veritabanı optimizasyonu tamamlandı.")
            return optimization_result

        except Exception as e:
            logging.error(f"Veritabanı optimizasyonu hatası: {e}")
            conn.rollback()
            return {'error': str(e)}
        finally:
            conn.close()

    def create_performance_indexes(self) -> Dict:
        """Performans indexleri oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("GRI performans indexleri oluşturuluyor...")

            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_gri_standards_category ON gri_standards(category)",
                "CREATE INDEX IF NOT EXISTS idx_gri_indicators_standard_id ON gri_indicators(standard_id)",
                "CREATE INDEX IF NOT EXISTS idx_gri_indicators_code ON gri_indicators(code)",
                "CREATE INDEX IF NOT EXISTS idx_gri_responses_company_indicator ON gri_responses(company_id, indicator_id)",
                "CREATE INDEX IF NOT EXISTS idx_gri_responses_period ON gri_responses(period)",
                "CREATE INDEX IF NOT EXISTS idx_gri_kpis_indicator_id ON gri_kpis(indicator_id)",
                "CREATE INDEX IF NOT EXISTS idx_gri_targets_year ON gri_targets(year)",
                "CREATE INDEX IF NOT EXISTS idx_gri_risks_level ON gri_risks(risk_level)",
                "CREATE INDEX IF NOT EXISTS idx_map_sdg_gri_sdg ON map_sdg_gri(sdg_indicator_code)",
                "CREATE INDEX IF NOT EXISTS idx_map_gri_tsrs_gri ON map_gri_tsrs(gri_disclosure)"
            ]

            created_indexes = []

            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    index_name = index_sql.split("idx_")[1].split(" ")[0]
                    created_indexes.append(index_name)
                except Exception as e:
                    logging.error(f"Index oluşturma hatası ({index_sql}): {e}")

            conn.commit()

            result = {
                'created_indexes': created_indexes,
                'total_indexes': len(created_indexes)
            }

            logging.info(f"{len(created_indexes)} GRI performans indexi oluşturuldu.")
            return result

        except Exception as e:
            logging.error(f"Index oluşturma hatası: {e}")
            conn.rollback()
            return {'error': str(e)}
        finally:
            conn.close()

# Global cache instance
gri_cache = GRIPerformanceCache()

def get_gri_cache() -> GRIPerformanceCache:
    """Global GRI cache instance'ını getir"""
    return gri_cache

def optimize_gri_database() -> Dict:
    """GRI veritabanı optimizasyonu fonksiyonu"""
    cache = get_gri_cache()
    return cache.optimize_database()

def create_gri_performance_indexes() -> Dict:
    """GRI performans indexleri oluşturma fonksiyonu"""
    cache = get_gri_cache()
    return cache.create_performance_indexes()

def get_gri_cache_stats() -> Dict:
    """GRI cache istatistikleri fonksiyonu"""
    cache = get_gri_cache()
    return cache.get_cache_stats()

if __name__ == "__main__":
    # Test cache sistemi
    cache = get_gri_cache()

    logging.info("=== GRI Performance Cache Test ===")

    # Cache istatistikleri
    stats = cache.get_cache_stats()
    logging.info(f"Cache boyutu: {stats['cache_size']}")
    logging.info(f"Geçerli kayıtlar: {stats['valid_entries']}")
    logging.info(f"Cache hit oranı: {stats['cache_hit_rate']:.2f}%")

    # Performans indexleri oluştur
    index_result = create_gri_performance_indexes()
    logging.info(f"Oluşturulan indexler: {index_result.get('created_indexes', [])}")

    # Veritabanı optimizasyonu
    opt_result = optimize_gri_database()
    logging.info(f"Optimizasyon tamamlandı: {opt_result.get('analyze_completed', False)}")

    # Cache'li sorgu testi
    logging.info("\nCache'li sorgu testi...")

    start_time = time.time()
    standards = cache.get_gri_standards_cached()
    query_time = time.time() - start_time
    logging.info(f"Standartlar sorgusu: {query_time:.3f}s, {len(standards)} kayıt")

    start_time = time.time()
    indicators = cache.get_gri_indicators_cached()
    query_time = time.time() - start_time
    logging.info(f"Göstergeler sorgusu: {query_time:.3f}s, {len(indicators)} kayıt")

    # Cache istatistikleri (güncellenmiş)
    stats = cache.get_cache_stats()
    logging.info("\nGüncellenmiş cache istatistikleri:")
    logging.info(f"Toplam sorgu: {stats['performance_stats']['total_queries']}")
    logging.info(f"Cache hit: {stats['performance_stats']['cache_hits']}")
    logging.info(f"Cache miss: {stats['performance_stats']['cache_misses']}")
    logging.info(f"Ortalama sorgu süresi: {stats['performance_stats']['avg_query_time']:.3f}s")
