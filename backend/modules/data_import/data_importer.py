import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Import Sistemi
Excel ve CSV formatlarından toplu veri yükleme
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


class DataImporter:
    """Veri import işlemlerini yöneten sınıf"""

    def __init__(self, db_path: str) -> None:
        """
        Args:
            db_path: Veritabanı yolu
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Veritabanı tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Import işlemleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                import_type TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT,
                status TEXT DEFAULT 'pending',
                total_rows INTEGER DEFAULT 0,
                successful_rows INTEGER DEFAULT 0,
                failed_rows INTEGER DEFAULT 0,
                error_log TEXT,
                imported_by INTEGER,
                imported_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Import hataları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                import_id INTEGER NOT NULL,
                row_number INTEGER,
                error_type TEXT,
                error_message TEXT,
                row_data TEXT,
                created_at TEXT,
                FOREIGN KEY (import_id) REFERENCES data_imports(id)
            )
        """)

        # Import mapping tablosu (sütun eşleştirmeleri)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mapping_name TEXT UNIQUE NOT NULL,
                import_type TEXT NOT NULL,
                column_mappings TEXT NOT NULL,
                transformation_rules TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    STANDARD_KEY_MAP = {
        'Gösterge Kodu': 'indicator_code',
        'Kod': 'indicator_code',
        'Gösterge Adı': 'indicator_name',
        'Başlık': 'title',
        'Açıklama': 'description',
        'Kategori': 'category',
        'Alt Kategori': 'sub_category',
        'Metrik': 'metric',
        'Metrik Adı': 'metric_name',
        'Değer': 'value',
        'Birim': 'unit',
        'Yıl': 'year',
        'Tarih': 'date',
        'Lokasyon': 'location',
        'Departman': 'department',
        'Durum': 'status',
        'Hedef Tarih': 'due_date',
        'Sorumlu': 'responsible',
        'Sorumlu Modül': 'module',
        'Standard': 'standard'
    }

    TYPE_RULES = {
        'value': 'float',
        'year': 'int',
        'date': 'date',
        'due_date': 'date'
    }

    REQUIRED_FIELDS_BY_CONTEXT = {
        'metric_row': ['metric_name', 'value', 'unit'],
        'action_row': ['standard', 'module', 'due_date', 'status']
    }

    # ============================================
    # DOSYA OKUMA
    # ============================================

    def read_excel(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Excel dosyasını oku
        
        Args:
            file_path: Dosya yolu
            sheet_name: Sayfa adı (opsiyonel, ilk sayfa okunur)
        
        Returns:
            DataFrame
        """
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)

            return df

        except Exception as e:
            raise Exception(f"Excel okuma hatası: {e}")

    def read_csv(self, file_path: str, encoding: str = 'utf-8',
                 delimiter: str = ',') -> pd.DataFrame:
        """
        CSV dosyasını oku
        
        Args:
            file_path: Dosya yolu
            encoding: Karakter kodlaması
            delimiter: Ayırıcı karakter
        
        Returns:
            DataFrame
        """
        try:
            df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
            return df

        except Exception:
            # Farklı encoding dene
            try:
                df = pd.read_csv(file_path, encoding='latin-1', delimiter=delimiter)
                return df
            except Exception as e:
                raise Exception(f"CSV okuma hatası: {e}")

    def get_excel_sheets(self, file_path: str) -> List[str]:
        """Excel dosyasındaki sayfa adlarını al"""
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            raise Exception(f"Sayfa adları alınamadı: {e}")

    def preview_data(self, file_path: str, rows: int = 10) -> Tuple[pd.DataFrame, List[str]]:
        """
        Dosya önizlemesi
        
        Args:
            file_path: Dosya yolu
            rows: Önizleme satır sayısı
        
        Returns:
            (DataFrame önizleme, sütun adları)
        """
        # Dosya tipine göre oku
        ext = os.path.splitext(file_path)[1].lower()

        if ext in ['.xlsx', '.xls']:
            df = self.read_excel(file_path)
        elif ext == '.csv':
            df = self.read_csv(file_path)
        else:
            raise Exception(f"Desteklenmeyen dosya tipi: {ext}")

        return df.head(rows), list(df.columns)

    def _normalize_record(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        out = {}
        for k, v in rec.items():
            nk = self.STANDARD_KEY_MAP.get(k, k)
            out[nk] = v
        for key, t in self.TYPE_RULES.items():
            if key in out and out[key] is not None:
                try:
                    if t == 'int':
                        out[key] = int(float(out[key]))
                    elif t == 'float':
                        out[key] = float(out[key])
                    elif t == 'date':
                        out[key] = pd.to_datetime(out[key]).strftime('%Y-%m-%d')
                except Exception as e:
                    # Tip dönüşüm hatası, yoksay
                    logging.error(f"Silent error caught: {str(e)}")
        return out

    def _validate_record(self, rec: Dict[str, Any]) -> Tuple[bool, str]:
        ctx = 'action_row' if ('status' in rec or 'due_date' in rec) else 'metric_row'
        req = self.REQUIRED_FIELDS_BY_CONTEXT.get(ctx, [])
        for r in req:
            if r not in rec or rec.get(r) in [None, '']:
                return False, f"Eksik alan: {r}"
        return True, ''

    def normalize_file(self, file_path: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[1].lower()
        rows = []
        errors: List[str] = []
        try:
            if ext in ['.json']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    data = [data]
                for rec in data:
                    nrec = self._normalize_record(rec)
                    ok, msg = self._validate_record(nrec)
                    if not ok:
                        errors.append(msg)
                    rows.append(nrec)
                out_path = file_path.replace('.json', '_normalized.json')
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(rows, f, ensure_ascii=False, indent=2)
            elif ext in ['.csv']:
                df = self.read_csv(file_path)
                for _, row in df.iterrows():
                    rec = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
                    nrec = self._normalize_record(rec)
                    ok, msg = self._validate_record(nrec)
                    if not ok:
                        errors.append(msg)
                    rows.append(nrec)
                import pandas as pd
                ndf = pd.DataFrame(rows)
                out_path = file_path.replace('.csv', '_normalized.csv')
                ndf.to_csv(out_path, index=False, encoding='utf-8-sig')
            else:
                return {'ok': False, 'error': 'Desteklenmeyen format'}
            return {'ok': True, 'count': len(rows), 'errors': errors}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def normalize_company_dir(self, company_id: int) -> Dict[str, Any]:
        base = os.path.join('data', 'companies', str(company_id))
        os.makedirs(base, exist_ok=True)
        processed = 0
        all_errors: List[str] = []
        for name in os.listdir(base):
            fp = os.path.join(base, name)
            if os.path.isfile(fp) and (fp.lower().endswith('.json') or fp.lower().endswith('.csv')):
                r = self.normalize_file(fp)
                if r.get('ok'):
                    processed += r.get('count', 0)
                    all_errors.extend(r.get('errors', []))
        return {'processed': processed, 'errors': all_errors}

    # ============================================
    # VERİ IMPORT
    # ============================================

    def import_data(self, company_id: int, file_path: str, import_type: str,
                   column_mapping: Dict[str, str],
                   target_table: str,
                   transformation_rules: Optional[Dict[str, Any]] = None,
                   validate_fn: Optional[callable] = None,
                   imported_by: Optional[int] = None) -> Dict:
        """
        Veriyi import et
        
        Args:
            company_id: Şirket ID
            file_path: Dosya yolu
            import_type: Import tipi (gri, tsrs, sdg, environmental, social, economic)
            column_mapping: Sütun eşleştirmeleri {excel_column: db_column}
            target_table: Hedef tablo adı
            transformation_rules: Dönüşüm kuralları
            validate_fn: Validasyon fonksiyonu
            imported_by: Import eden kullanıcı ID
        
        Returns:
            {
                'import_id': int,
                'total_rows': int,
                'successful': int,
                'failed': int,
                'errors': List[str]
            }
        """
        # Import kaydı oluştur
        import_id = self._create_import_record(
            company_id=company_id,
            file_path=file_path,
            import_type=import_type,
            imported_by=imported_by
        )

        try:
            # Dosyayı oku
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.xlsx', '.xls']:
                df = self.read_excel(file_path)
            elif ext == '.csv':
                df = self.read_csv(file_path)
            else:
                raise Exception(f"Desteklenmeyen dosya tipi: {ext}")

            total_rows = len(df)
            successful_rows = 0
            failed_rows = 0
            errors = []

            # Her satırı işle
            for index, row in df.iterrows():
                try:
                    # Sütunları eşleştir
                    mapped_data = {}
                    for excel_col, db_col in column_mapping.items():
                        if excel_col in row:
                            value = row[excel_col]

                            # NaN kontrolü
                            if pd.isna(value):
                                value = None

                            # Dönüşüm kuralları uygula
                            if transformation_rules and db_col in transformation_rules:
                                value = self._apply_transformation(value, transformation_rules[db_col])

                            mapped_data[db_col] = value

                    # Company ID ekle
                    mapped_data['company_id'] = company_id

                    # Validasyon
                    if validate_fn:
                        is_valid, error_msg = validate_fn(mapped_data, index + 2)  # +2 for header and 1-based index
                        if not is_valid:
                            raise ValueError(error_msg)

                    # Veritabanına kaydet
                    self._insert_row(target_table, mapped_data)
                    successful_rows += 1

                except Exception as e:
                    failed_rows += 1
                    error_msg = str(e)
                    errors.append(f"Satır {index + 2}: {error_msg}")

                    # Hata kaydı
                    self._log_import_error(
                        import_id=import_id,
                        row_number=index + 2,
                        error_type='import_error',
                        error_message=error_msg,
                        row_data=json.dumps(row.to_dict(), default=str, ensure_ascii=False)
                    )

            # Import kaydını güncelle
            self._update_import_record(
                import_id=import_id,
                status='completed' if failed_rows == 0 else 'completed_with_errors',
                total_rows=total_rows,
                successful_rows=successful_rows,
                failed_rows=failed_rows
            )

            return {
                'import_id': import_id,
                'total_rows': total_rows,
                'successful': successful_rows,
                'failed': failed_rows,
                'errors': errors
            }

        except Exception as e:
            # Import hatası
            self._update_import_record(
                import_id=import_id,
                status='failed',
                error_log=str(e)
            )

            raise Exception(f"Import hatası: {e}")

    def _apply_transformation(self, value: Any, rules: Dict) -> Any:
        """Dönüşüm kurallarını uygula"""
        if value is None:
            return None

        # Tip dönüşümü
        if 'type' in rules:
            target_type = rules['type']
            try:
                if target_type == 'int':
                    value = int(float(value))
                elif target_type == 'float':
                    value = float(value)
                elif target_type == 'str':
                    value = str(value)
                elif target_type == 'date':
                    value = pd.to_datetime(value).strftime('%Y-%m-%d')
                elif target_type == 'datetime':
                    value = pd.to_datetime(value).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

        # Değer eşleştirme
        if 'mapping' in rules:
            value = rules['mapping'].get(value, value)

        # Formül
        if 'formula' in rules:
            # Basit formül desteği (örn: value * 100)
            try:
                value = eval(rules['formula'].replace('value', str(value)))
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

        # Varsayılan değer
        if value is None and 'default' in rules:
            value = rules['default']

        return value

    def _insert_row(self, table: str, data: Dict) -> None:
        """Veritabanına satır ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Ekleme tarihini ekle
        if 'created_at' not in data:
            data['created_at'] = datetime.now().isoformat()

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        cursor.execute(query, list(data.values()))

        conn.commit()
        conn.close()

    def _create_import_record(self, company_id: int, file_path: str,
                             import_type: str, imported_by: Optional[int]) -> int:
        """Import kaydı oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO data_imports 
            (company_id, import_type, file_name, file_path, status, imported_by, imported_at)
            VALUES (?, ?, ?, ?, 'in_progress', ?, ?)
        """, (
            company_id,
            import_type,
            os.path.basename(file_path),
            file_path,
            imported_by,
            datetime.now().isoformat()
        ))

        import_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return import_id

    def _update_import_record(self, import_id: int, status: str,
                             total_rows: int = 0, successful_rows: int = 0,
                             failed_rows: int = 0, error_log: str = None) -> None:
        """Import kaydını güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE data_imports 
            SET status = ?, total_rows = ?, successful_rows = ?, failed_rows = ?,
                error_log = ?, completed_at = ?
            WHERE id = ?
        """, (
            status,
            total_rows,
            successful_rows,
            failed_rows,
            error_log,
            datetime.now().isoformat(),
            import_id
        ))

        conn.commit()
        conn.close()

    def _log_import_error(self, import_id: int, row_number: int,
                         error_type: str, error_message: str,
                         row_data: str) -> None:
        """Import hatasını kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO import_errors 
            (import_id, row_number, error_type, error_message, row_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            import_id,
            row_number,
            error_type,
            error_message,
            row_data,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    # ============================================
    # MAPPING YÖNETİMİ
    # ============================================

    def save_mapping(self, mapping_name: str, import_type: str,
                    column_mappings: Dict[str, str],
                    transformation_rules: Optional[Dict] = None) -> bool:
        """
        Sütun eşleştirmesini kaydet
        
        Args:
            mapping_name: Mapping adı
            import_type: Import tipi
            column_mappings: Sütun eşleştirmeleri
            transformation_rules: Dönüşüm kuralları
        
        Returns:
            Başarılı ise True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO import_mappings 
                (mapping_name, import_type, column_mappings, transformation_rules, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                mapping_name,
                import_type,
                json.dumps(column_mappings, ensure_ascii=False),
                json.dumps(transformation_rules, ensure_ascii=False) if transformation_rules else None,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Mapping kaydetme hatası: {e}")
            return False

    def get_mapping(self, mapping_name: str) -> Optional[Dict]:
        """Kaydedilmiş mapping'i al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT column_mappings, transformation_rules
                FROM import_mappings
                WHERE mapping_name = ?
            """, (mapping_name,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'column_mappings': json.loads(result[0]),
                    'transformation_rules': json.loads(result[1]) if result[1] else None
                }

            return None

        except Exception as e:
            logging.error(f"Mapping alma hatası: {e}")
            return None

    def list_mappings(self, import_type: Optional[str] = None) -> List[Dict]:
        """Mapping'leri listele"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if import_type:
                cursor.execute("""
                    SELECT mapping_name, import_type, created_at
                    FROM import_mappings
                    WHERE import_type = ?
                    ORDER BY mapping_name
                """, (import_type,))
            else:
                cursor.execute("""
                    SELECT mapping_name, import_type, created_at
                    FROM import_mappings
                    ORDER BY import_type, mapping_name
                """)

            mappings = []
            for row in cursor.fetchall():
                mappings.append({
                    'name': row[0],
                    'type': row[1],
                    'created_at': row[2]
                })

            conn.close()
            return mappings

        except Exception as e:
            logging.error(f"Mapping listeleme hatası: {e}")
            return []

    # ============================================
    # IMPORT GEÇMİŞİ
    # ============================================

    def get_import_history(self, company_id: int, limit: int = 50) -> List[Dict]:
        """Import geçmişini al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, import_type, file_name, status, total_rows, 
                       successful_rows, failed_rows, imported_at, completed_at
                FROM data_imports
                WHERE company_id = ?
                ORDER BY imported_at DESC
                LIMIT ?
            """, (company_id, limit))

            history = []
            for row in cursor.fetchall():
                history.append({
                    'id': row[0],
                    'type': row[1],
                    'file_name': row[2],
                    'status': row[3],
                    'total_rows': row[4],
                    'successful_rows': row[5],
                    'failed_rows': row[6],
                    'imported_at': row[7],
                    'completed_at': row[8]
                })

            conn.close()
            return history

        except Exception as e:
            logging.error(f"Geçmiş alma hatası: {e}")
            return []

    def get_import_errors(self, import_id: int) -> List[Dict]:
        """Import hatalarını al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT row_number, error_type, error_message, row_data
                FROM import_errors
                WHERE import_id = ?
                ORDER BY row_number
            """, (import_id,))

            errors = []
            for row in cursor.fetchall():
                errors.append({
                    'row_number': row[0],
                    'error_type': row[1],
                    'error_message': row[2],
                    'row_data': json.loads(row[3]) if row[3] else None
                })

            conn.close()
            return errors

        except Exception as e:
            logging.error(f"Hata listeleme hatası: {e}")
            return []

    # ============================================
    # ŞABLON OLUŞTURMA
    # ============================================

    def create_template(self, columns: List[str], sample_data: List[List] = None,
                       output_path: str = None, format: str = 'excel') -> bool:
        """
        Import şablonu oluştur
        
        Args:
            columns: Sütun adları
            sample_data: Örnek veriler
            output_path: Çıktı dosya yolu
            format: Format (excel veya csv)
        
        Returns:
            Başarılı ise True
        """
        try:
            # DataFrame oluştur
            if sample_data:
                df = pd.DataFrame(sample_data, columns=columns)
            else:
                df = pd.DataFrame(columns=columns)

            # Dosyaya kaydet
            if format == 'excel':
                if not output_path:
                    output_path = 'import_template.xlsx'
                df.to_excel(output_path, index=False)
            else:
                if not output_path:
                    output_path = 'import_template.csv'
                df.to_csv(output_path, index=False, encoding='utf-8-sig')

            return True

        except Exception as e:
            logging.error(f"Şablon oluşturma hatası: {e}")
            return False


# ============================================
# VALİDASYON FONKSİYONLARI
# ============================================

def validate_gri_data(data: Dict, row_num: int) -> Tuple[bool, str]:
    """GRI veri validasyonu"""
    required_fields = ['indicator_code', 'value']

    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Zorunlu alan eksik: {field}"

    # Gösterge kodu formatı
    indicator_code = str(data['indicator_code'])
    if not indicator_code.startswith('GRI'):
        return False, f"Geçersiz GRI kodu: {indicator_code}"

    return True, ""


def validate_environmental_data(data: Dict, row_num: int) -> Tuple[bool, str]:
    """Çevresel veri validasyonu"""
    required_fields = ['metric_type', 'value', 'unit']

    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Zorunlu alan eksik: {field}"

    # Değer kontrolü
    try:
        value = float(data['value'])
        if value < 0:
            return False, "Değer negatif olamaz"
    except Exception:
        return False, "Geçersiz sayısal değer"

    return True, ""


def validate_social_data(data: Dict, row_num: int) -> Tuple[bool, str]:
    """Sosyal veri validasyonu"""
    required_fields = ['metric_name', 'value']

    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Zorunlu alan eksik: {field}"

    return True, ""

