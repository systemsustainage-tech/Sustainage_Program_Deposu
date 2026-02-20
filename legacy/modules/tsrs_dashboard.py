"""
TSRS Dashboard Modülü
Türkiye Sürdürülebilirlik Raporlama Standardı Dashboard
"""

from datetime import datetime
from typing import Dict, List

from core.db_manager import db_manager
from core.logger import sdg_logger
from config.database import DB_PATH


class TSRSDashboard:
    """TSRS Dashboard yöneticisi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """TSRS tablolarını oluştur"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # TSRS standartları tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tsrs_standards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL UNIQUE,
                        title TEXT NOT NULL,
                        description TEXT,
                        category TEXT NOT NULL,
                        subcategory TEXT,
                        requirement_level TEXT DEFAULT 'Mandatory',
                        reporting_frequency TEXT DEFAULT 'Annual',
                        effective_date DATE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # TSRS göstergeleri tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tsrs_indicators (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL UNIQUE,
                        title TEXT NOT NULL,
                        description TEXT,
                        unit TEXT,
                        methodology TEXT,
                        data_type TEXT DEFAULT 'text',
                        is_mandatory BOOLEAN DEFAULT 0,
                        is_quantitative BOOLEAN DEFAULT 0,
                        baseline_year INTEGER,
                        target_year INTEGER,
                        standard_id INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (standard_id) REFERENCES tsrs_standards(id)
                    )
                """)

                # TSRS yanıtları tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tsrs_responses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        indicator_id INTEGER NOT NULL,
                        reporting_period TEXT NOT NULL,
                        response_value TEXT,
                        numerical_value REAL,
                        unit TEXT,
                        methodology_used TEXT,
                        data_source TEXT,
                        reporting_status TEXT DEFAULT 'Draft',
                        evidence_url TEXT,
                        notes TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (indicator_id) REFERENCES tsrs_indicators(id)
                    )
                """)

                conn.commit()
                sdg_logger.log_info("TSRS tabloları oluşturuldu/doğrulandı", "tsrs_dashboard")

        except Exception as e:
            sdg_logger.log_error(e, "TSRS tabloları oluşturma", module="tsrs_dashboard")

    def get_dashboard_summary(self, company_id: int, period: int = 2024) -> Dict[str, any]:
        """TSRS dashboard özeti"""
        try:
            with db_manager.get_connection(read_only=True) as conn:
                cursor = conn.cursor()

                # Toplam standart sayısı
                cursor.execute("SELECT COUNT(*) FROM tsrs_standards")
                total_standards = cursor.fetchone()[0]

                # Toplam gösterge sayısı
                cursor.execute("SELECT COUNT(*) FROM tsrs_indicators")
                total_indicators = cursor.fetchone()[0]

                # Yanıtlanan gösterge sayısı
                cursor.execute("""
                    SELECT COUNT(DISTINCT indicator_id) 
                    FROM tsrs_responses 
                    WHERE company_id = ? AND reporting_period = ?
                """, (company_id, str(period)))
                answered_indicators = cursor.fetchone()[0]

                # Yanıt yüzdesi
                response_percentage = (answered_indicators / total_indicators * 100) if total_indicators > 0 else 0

                # Kategori bazında dağılım
                cursor.execute("""
                    SELECT category, COUNT(*) 
                    FROM tsrs_standards 
                    GROUP BY category
                """)
                category_distribution = dict(cursor.fetchall())

                # Son yanıtlar
                cursor.execute("""
                    SELECT r.reporting_period, r.reporting_status, COUNT(*) as count
                    FROM tsrs_responses r
                    WHERE r.company_id = ?
                    GROUP BY r.reporting_period, r.reporting_status
                    ORDER BY r.reporting_period DESC
                    LIMIT 10
                """, (company_id,))
                recent_responses = cursor.fetchall()

                return {
                    "total_standards": total_standards,
                    "total_indicators": total_indicators,
                    "answered_indicators": answered_indicators,
                    "response_percentage": round(response_percentage, 1),
                    "category_distribution": category_distribution,
                    "recent_responses": recent_responses,
                    "period": period
                }

        except Exception as e:
            sdg_logger.log_error(e, "TSRS dashboard özet alma", module="tsrs_dashboard")
            return {"error": str(e)}

    def get_category_standards(self, category: str) -> List[Dict]:
        """Kategoriye göre standartları getir"""
        try:
            with db_manager.get_connection(read_only=True) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, code, title, description, category, subcategory,
                           requirement_level, reporting_frequency
                    FROM tsrs_standards 
                    WHERE category = ?
                    ORDER BY code
                """, (category,))

                columns = [desc[0] for desc in cursor.description]
                standards = [dict(zip(columns, row)) for row in cursor.fetchall()]

                return standards

        except Exception as e:
            sdg_logger.log_error(e, f"TSRS standartları getirme: {category}", module="tsrs_dashboard")
            return []

    def get_indicators_by_standard(self, standard_id: int) -> List[Dict]:
        """Standarta göre göstergeleri getir"""
        try:
            with db_manager.get_connection(read_only=True) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, code, title, description, unit, methodology,
                           data_type, is_mandatory, is_quantitative
                    FROM tsrs_indicators 
                    WHERE standard_id = ?
                    ORDER BY code
                """, (standard_id,))

                columns = [desc[0] for desc in cursor.description]
                indicators = [dict(zip(columns, row)) for row in cursor.fetchall()]

                return indicators

        except Exception as e:
            sdg_logger.log_error(e, f"TSRS göstergeleri getirme: {standard_id}", module="tsrs_dashboard")
            return []

    def save_indicator_response(self, company_id: int, indicator_id: int,
                               reporting_period: str, response_data: Dict) -> bool:
        """Gösterge yanıtını kaydet"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Mevcut yanıtı kontrol et
                cursor.execute("""
                    SELECT id FROM tsrs_responses 
                    WHERE company_id = ? AND indicator_id = ? AND reporting_period = ?
                """, (company_id, indicator_id, reporting_period))

                existing = cursor.fetchone()

                if existing:
                    # Güncelle
                    cursor.execute("""
                        UPDATE tsrs_responses SET
                            response_value = ?, numerical_value = ?, unit = ?,
                            methodology_used = ?, data_source = ?, reporting_status = ?,
                            evidence_url = ?, notes = ?, updated_at = ?
                        WHERE id = ?
                    """, (
                        response_data.get('response_value', ''),
                        response_data.get('numerical_value'),
                        response_data.get('unit', ''),
                        response_data.get('methodology_used', ''),
                        response_data.get('data_source', ''),
                        response_data.get('reporting_status', 'Draft'),
                        response_data.get('evidence_url', ''),
                        response_data.get('notes', ''),
                        datetime.now(),
                        existing[0]
                    ))
                else:
                    # Yeni kayıt
                    cursor.execute("""
                        INSERT INTO tsrs_responses 
                        (company_id, indicator_id, reporting_period, response_value,
                         numerical_value, unit, methodology_used, data_source,
                         reporting_status, evidence_url, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        company_id, indicator_id, reporting_period,
                        response_data.get('response_value', ''),
                        response_data.get('numerical_value'),
                        response_data.get('unit', ''),
                        response_data.get('methodology_used', ''),
                        response_data.get('data_source', ''),
                        response_data.get('reporting_status', 'Draft'),
                        response_data.get('evidence_url', ''),
                        response_data.get('notes', '')
                    ))

                conn.commit()
                sdg_logger.log_info(f"TSRS yanıtı kaydedildi: {indicator_id}", "tsrs_dashboard")
                return True

        except Exception as e:
            sdg_logger.log_error(e, f"TSRS yanıtı kaydetme: {indicator_id}", module="tsrs_dashboard")
            return False

    def create_sample_data(self, company_id: int = 1) -> None:
        """
        DEPRECATED: Örnek veri oluşturma devre dışı bırakıldı.
        Gerçek veriler TSRSManager tarafından yönetilmektedir.
        """
        sdg_logger.log_info("create_sample_data çağrıldı ancak devre dışı bırakıldı (Gerçek veri zorunluluğu)", "tsrs_dashboard")
        return

