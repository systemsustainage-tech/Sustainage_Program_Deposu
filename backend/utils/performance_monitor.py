#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Monitor
Sistem performansını izleme ve optimizasyon aracı
"""

import logging
import os
import re
import sqlite3
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

import psutil
from config.database import DB_PATH


class PerformanceMonitor:
    """Sistem performans izleyicisi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self.monitoring = False
        self.monitor_thread = None
        self.performance_data = []
        self.lock = threading.Lock()

    def start_monitoring(self, interval: int = 5) -> None:
        """Performans izlemeyi başlat"""
        if self.monitoring:
            return

        self.monitoring = True
        self.stop_event = threading.Event()
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Performans izlemeyi durdur"""
        self.monitoring = False
        if hasattr(self, 'stop_event'):
            self.stop_event.set()
            
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def _monitor_loop(self, interval: int) -> None:
        """Performans izleme döngüsü"""
        while self.monitoring and not self.stop_event.is_set():
            try:
                data = self._collect_performance_data()
                with self.lock:
                    self.performance_data.append(data)
                    # Son 100 kaydı tut
                    if len(self.performance_data) > 100:
                        self.performance_data = self.performance_data[-100:]

                self.stop_event.wait(interval)
            except Exception:
                logging.exception("Performance monitoring error")
                self.stop_event.wait(interval)

    def _collect_performance_data(self) -> Dict:
        """Performans verilerini topla"""
        try:
            # CPU kullanımı
            cpu_percent = psutil.cpu_percent(interval=1)

            # Bellek kullanımı
            memory = psutil.virtual_memory()

            # Disk kullanımı
            disk = psutil.disk_usage('/')

            # Veritabanı boyutu
            db_size = 0
            if os.path.exists(self.db_path):
                db_size = os.path.getsize(self.db_path)

            # Aktif bağlantı sayısı
            active_connections = 0
            try:
                conn = sqlite3.connect(self.db_path, timeout=5)
                cursor = conn.cursor()
                cursor.execute("PRAGMA database_list")
                active_connections = len(cursor.fetchall())
                conn.close()
            except Exception as e:
                logging.warning("Active connection check failed: %s", e)

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "memory_available_mb": memory.available / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used / 1024 / 1024 / 1024,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "db_size_mb": db_size / 1024 / 1024,
                "active_connections": active_connections
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def get_performance_summary(self) -> Dict:
        """Performans özetini al"""
        with self.lock:
            if not self.performance_data:
                return {"error": "No performance data available"}

            recent_data = self.performance_data[-10:]  # Son 10 kayıt

            # Ortalama değerleri hesapla
            cpu_values = [d.get("cpu_percent", 0) for d in recent_data if "cpu_percent" in d]
            memory_values = [d.get("memory_percent", 0) for d in recent_data if "memory_percent" in d]

            return {
                "avg_cpu_percent": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "avg_memory_percent": sum(memory_values) / len(memory_values) if memory_values else 0,
                "current_cpu": cpu_values[-1] if cpu_values else 0,
                "current_memory": memory_values[-1] if memory_values else 0,
                "data_points": len(self.performance_data),
                "monitoring_active": self.monitoring
            }

    def get_database_stats(self) -> Dict:
        """Veritabanı istatistiklerini al"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=5)
            cursor = conn.cursor()

            # Tablo sayıları
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            # Toplam kayıt sayısı
            total_records = 0
            table_stats = {}

            for table in tables:
                table_name = table[0]
                try:
                    if re.fullmatch(r"[A-Za-z0-9_]+", table_name):
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        total_records += count
                        table_stats[table_name] = count
                    else:
                        table_stats[table_name] = 0
                except Exception as e:
                    logging.warning("Table stats failed for %s: %s", table_name, e)
                    table_stats[table_name] = 0

            # Veritabanı boyutu
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0

            conn.close()

            return {
                "total_tables": len(tables),
                "total_records": total_records,
                "db_size_mb": db_size / 1024 / 1024,
                "table_stats": table_stats
            }

        except Exception as e:
            return {"error": str(e)}

    def optimize_database(self) -> Dict:
        """Veritabanını optimize et"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()

            # Optimizasyon komutları
            optimizations = []

            # PRAGMA optimize
            cursor.execute("PRAGMA optimize")
            optimizations.append("PRAGMA optimize executed")

            # VACUUM (dikkatli kullan)
            # cursor.execute("VACUUM")
            # optimizations.append("VACUUM executed")

            # ANALYZE
            cursor.execute("ANALYZE")
            optimizations.append("ANALYZE executed")

            # Cache temizleme
            cursor.execute("PRAGMA cache_size=10000")
            optimizations.append("Cache size optimized")

            conn.commit()
            conn.close()

            return {
                "success": True,
                "optimizations": optimizations,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_recommendations(self) -> List[str]:
        """Performans önerilerini al"""
        recommendations = []

        try:
            summary = self.get_performance_summary()
            db_stats = self.get_database_stats()

            # CPU önerileri
            if summary.get("avg_cpu_percent", 0) > 80:
                recommendations.append("CPU kullanımı yüksek. Daha az eşzamanlı işlem yapın.")

            # Bellek önerileri
            if summary.get("avg_memory_percent", 0) > 85:
                recommendations.append("Bellek kullanımı yüksek. Uygulamayı yeniden başlatmayı düşünün.")

            # Veritabanı önerileri
            if db_stats.get("db_size_mb", 0) > 100:
                recommendations.append("Veritabanı boyutu büyük. VACUUM işlemi yapmayı düşünün.")

            if db_stats.get("total_records", 0) > 100000:
                recommendations.append("Çok fazla kayıt var. Eski verileri arşivlemeyi düşünün.")

            # Genel öneriler
            if not recommendations:
                recommendations.append("Sistem performansı iyi görünüyor.")

        except Exception as e:
            recommendations.append(f"Performans analizi hatası: {e}")

        return recommendations

# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Global performance monitor instance'ını al"""
    global _performance_monitor
    if not _performance_monitor:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def start_performance_monitoring(interval: int = 5) -> None:
    """Performans izlemeyi başlat"""
    monitor = get_performance_monitor()
    monitor.start_monitoring(interval)

def stop_performance_monitoring() -> None:
    """Performans izlemeyi durdur"""
    monitor = get_performance_monitor()
    monitor.stop_monitoring()
