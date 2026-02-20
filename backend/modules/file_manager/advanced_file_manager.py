#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Dosya Yönetim Sistemi
Çoklu dosya yükleme, klasör yapısı, etiketleme, versiyon kontrolü
"""

import logging
import hashlib
import mimetypes
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from backend.core.base_manager import BaseTenantManager


class AdvancedFileManager(BaseTenantManager):
    """Gelişmiş dosya yönetimi sınıfı"""

    def __init__(self, db_path: str, base_upload_dir: str = None, company_id: Optional[int] = None) -> None:
        """
        Args:
            db_path: Veritabanı yolu
            base_upload_dir: Dosya yükleme klasörü
            company_id: Şirket ID (Tenant Isolation)
        """
        super().__init__(db_path, company_id)
        if base_upload_dir:
             self.base_upload_dir = base_upload_dir
        else:
             # Default to uploads folder in project root
             root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
             self.base_upload_dir = os.path.join(root_dir, 'uploads')
             
        self._init_database()
        self._ensure_table_schema()
        self._ensure_upload_directory()

    def _ensure_table_schema(self) -> None:
        """Mevcut tabloların şemasını kontrol et ve eksik kolonları ekle (Migration)"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check tables for company_id
                tables_to_check = ['file_shares', 'file_folders', 'file_tags', 'files', 'file_tag_relations', 'file_metadata']
                
                for table in tables_to_check:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    # If table exists (columns not empty) and company_id is missing
                    if columns and 'company_id' not in columns:
                        logging.info(f"Migrating {table} table: Adding company_id column")
                        try:
                            # company_id is required, defaulting to 1 for migration
                            cursor.execute(f"ALTER TABLE {table} ADD COLUMN company_id INTEGER NOT NULL DEFAULT 1 REFERENCES companies(id)")
                            conn.commit()
                        except Exception as migration_error:
                             if "duplicate column name" in str(migration_error).lower():
                                 logging.warning(f"Column company_id already exists in {table} (race condition ignored)")
                             else:
                                 raise migration_error
                    
        except Exception as e:
            logging.error(f"Error migrating tables: {e}")

    def _init_database(self) -> None:
        """Veritabanı tablolarını oluştur"""
        # Dosyalar tablosu
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                folder_id INTEGER,
                file_name TEXT NOT NULL,
                original_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                mime_type TEXT,
                checksum TEXT,
                version INTEGER DEFAULT 1,
                parent_version_id INTEGER,
                description TEXT,
                uploaded_by INTEGER,
                uploaded_at TEXT,
                updated_at TEXT,
                is_deleted INTEGER DEFAULT 0,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (folder_id) REFERENCES file_folders(id),
                FOREIGN KEY (parent_version_id) REFERENCES files(id)
            )
        """)

        # Klasörler tablosu
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS file_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                parent_folder_id INTEGER,
                folder_name TEXT NOT NULL,
                folder_path TEXT NOT NULL,
                description TEXT,
                created_by INTEGER,
                created_at TEXT,
                updated_at TEXT,
                is_deleted INTEGER DEFAULT 0,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (parent_folder_id) REFERENCES file_folders(id)
            )
        """)

        # Dosya etiketleri tablosu
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS file_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                tag_name TEXT NOT NULL,
                tag_color TEXT DEFAULT '#3498db',
                created_at TEXT,
                UNIQUE(company_id, tag_name),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Dosya-etiket ilişkileri tablosu
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS file_tag_relations (
                file_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                created_at TEXT,
                PRIMARY KEY (file_id, tag_id),
                FOREIGN KEY (file_id) REFERENCES files(id),
                FOREIGN KEY (tag_id) REFERENCES file_tags(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Dosya metadata tablosu (ek bilgiler için)
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                meta_key TEXT NOT NULL,
                meta_value TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Dosya paylaşım tablosu
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS file_shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                shared_with_user_id INTEGER,
                shared_with_company_id INTEGER,
                permission TEXT DEFAULT 'view',
                shared_by INTEGER,
                shared_at TEXT,
                expires_at TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # İndeksler
        self.execute_update("""
            CREATE INDEX IF NOT EXISTS idx_files_company 
            ON files(company_id, is_deleted)
        """)

        self.execute_update("""
            CREATE INDEX IF NOT EXISTS idx_files_folder 
            ON files(folder_id, is_deleted)
        """)

        self.execute_update("""
            CREATE INDEX IF NOT EXISTS idx_files_version 
            ON files(parent_version_id)
        """)

    def _ensure_upload_directory(self) -> None:
        """Yükleme klasörünü oluştur"""
        os.makedirs(self.base_upload_dir, exist_ok=True)

    def _calculate_checksum(self, file_path: str) -> str:
        """Dosya checksum'ını hesapla"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _verify_file_ownership(self, file_id: int, company_id: Optional[int] = None) -> bool:
        """Dosyanın şirkete ait olduğunu doğrula"""
        try:
            # execute_query will enforce company_id if provided or from context
            rows = self.execute_query("SELECT id FROM files WHERE id = ?", (file_id,), company_id=company_id)
            return len(rows) > 0
        except Exception:
            return False

    # ============================================
    # KLASÖR YÖNETİMİ
    # ============================================

    def create_folder(self, company_id: int, folder_name: str,
                     parent_folder_id: Optional[int] = None,
                     description: str = "", created_by: Optional[int] = None) -> Optional[int]:
        """
        Yeni klasör oluştur
        
        Args:
            company_id: Şirket ID
            folder_name: Klasör adı
            parent_folder_id: Üst klasör ID (opsiyonel)
            description: Açıklama
            created_by: Oluşturan kullanıcı ID
        
        Returns:
            Oluşturulan klasör ID veya None
        """
        try:
            # Klasör yolunu oluştur
            if parent_folder_id:
                parent_path = self.get_folder_path(parent_folder_id)
                folder_path = os.path.join(parent_path, folder_name) if parent_path else None
                if not folder_path:
                    # Fallback
                     folder_path = os.path.join(
                        self.base_upload_dir,
                        f"company_{company_id}",
                        folder_name
                    )
            else:
                folder_path = os.path.join(
                    self.base_upload_dir,
                    f"company_{company_id}",
                    folder_name
                )

            # Fiziksel klasörü oluştur
            os.makedirs(folder_path, exist_ok=True)

            # Veritabanına kaydet
            folder_id = self.execute_update("""
                INSERT INTO file_folders 
                (company_id, parent_folder_id, folder_name, folder_path, description, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                parent_folder_id,
                folder_name,
                folder_path,
                description,
                created_by,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ), company_id=company_id)

            return folder_id

        except Exception as e:
            logging.error(f"Klasör oluşturma hatası: {e}")
            return None

    def get_folder_path(self, folder_id: int, company_id: Optional[int] = None) -> Optional[str]:
        """Klasör yolunu al"""
        try:
            # company_id opsiyonel, eğer verilirse tenant isolation sağlar
            query = "SELECT folder_path FROM file_folders WHERE id = ?"
            params = [folder_id]
            
            kwargs = {}
            if company_id is not None:
                kwargs['company_id'] = company_id
            
            rows = self.execute_query(query, tuple(params), **kwargs)
            return rows[0]['folder_path'] if rows else None

        except Exception as e:
            logging.error(f"Klasör yolu alma hatası: {e}")
            return None

    def list_folders(self, company_id: int, parent_folder_id: Optional[int] = None) -> List[Dict]:
        """
        Klasörleri listele
        
        Args:
            company_id: Şirket ID
            parent_folder_id: Üst klasör ID (None = kök klasörler)
        
        Returns:
            Klasör listesi
        """
        try:
            if parent_folder_id is None:
                rows = self.execute_query("""
                    SELECT id, folder_name, description, created_at, 
                           (SELECT COUNT(*) FROM files WHERE folder_id = file_folders.id AND is_deleted = 0) as file_count
                    FROM file_folders
                    WHERE company_id = ? AND parent_folder_id IS NULL AND is_deleted = 0
                    ORDER BY folder_name
                """, (company_id,), company_id=company_id)
            else:
                rows = self.execute_query("""
                    SELECT id, folder_name, description, created_at,
                           (SELECT COUNT(*) FROM files WHERE folder_id = file_folders.id AND is_deleted = 0) as file_count
                    FROM file_folders
                    WHERE company_id = ? AND parent_folder_id = ? AND is_deleted = 0
                    ORDER BY folder_name
                """, (company_id, parent_folder_id), company_id=company_id)

            folders = []
            for row in rows:
                folders.append({
                    'id': row['id'],
                    'name': row['folder_name'],
                    'description': row['description'],
                    'created_at': row['created_at'],
                    'file_count': row['file_count']
                })

            return folders

        except Exception as e:
            logging.error(f"Klasör listeleme hatası: {e}")
            return []

    def delete_folder(self, folder_id: int, company_id: int) -> bool:
        """
        Klasörü sil (soft delete)
        
        Args:
            folder_id: Klasör ID
            company_id: Şirket ID (Güvenlik için zorunlu)
        
        Returns:
            Başarılı ise True
        """
        try:
            # Klasörün şirkete ait olduğunu doğrula
            rows = self.execute_query(
                "SELECT id FROM file_folders WHERE id = ? AND company_id = ?", 
                (folder_id, company_id),
                company_id=company_id
            )
            
            if not rows:
                logging.warning(f"Delete Folder: Folder {folder_id} not found or access denied for company {company_id}")
                return False

            timestamp = datetime.now().isoformat()

            # Soft delete folder
            self.execute_update("""
                UPDATE file_folders 
                SET is_deleted = 1, updated_at = ?
                WHERE id = ? AND company_id = ?
            """, (timestamp, folder_id, company_id), company_id=company_id)

            # İçindeki dosyaları da sil
            self.execute_update("""
                UPDATE files 
                SET is_deleted = 1, updated_at = ?
                WHERE folder_id = ? AND company_id = ?
            """, (timestamp, folder_id, company_id), company_id=company_id)

            return True

        except Exception as e:
            logging.error(f"Klasör silme hatası: {e}")
            return False

    # ============================================
    # DOSYA YÖNETİMİ
    # ============================================

    def upload_file(self, company_id: int, source_path: str,
                   folder_id: Optional[int] = None,
                   description: str = "",
                   tags: List[str] = None,
                   metadata: Dict[str, str] = None,
                   uploaded_by: Optional[int] = None) -> Optional[int]:
        """
        Dosya yükle
        
        Args:
            company_id: Şirket ID
            source_path: Kaynak dosya yolu
            folder_id: Hedef klasör ID
            description: Açıklama
            tags: Etiketler listesi
            metadata: Ek metadata
            uploaded_by: Yükleyen kullanıcı ID
        
        Returns:
            Dosya ID veya None
        """
        try:
            # Dosya bilgilerini al
            original_name = os.path.basename(source_path)
            file_size = os.path.getsize(source_path)
            mime_type, _ = mimetypes.guess_type(source_path)
            file_ext = os.path.splitext(original_name)[1]

            # Benzersiz dosya adı oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_name = f"{timestamp}_{hashlib.sha256(original_name.encode()).hexdigest()[:12]}{file_ext}"

            # Hedef yolu belirle
            if folder_id:
                folder_path = self.get_folder_path(folder_id, company_id=company_id)
                if not folder_path:
                    # Fallback if get_folder_path fails or returns None
                    # But get_folder_path might fail if context is missing.
                    # We should probably trust get_folder_path or handle None.
                    logging.warning(f"Upload: Folder path not found for id {folder_id}")
                    return None
                dest_path = os.path.join(folder_path, unique_name)
            else:
                company_dir = os.path.join(self.base_upload_dir, f"company_{company_id}")
                os.makedirs(company_dir, exist_ok=True)
                dest_path = os.path.join(company_dir, unique_name)

            # Dosyayı kopyala
            shutil.copy2(source_path, dest_path)

            # Checksum hesapla
            checksum = self._calculate_checksum(dest_path)

            # Veritabanına kaydet
            # Use execute_update with company_id context
            file_id = self.execute_update("""
                INSERT INTO files 
                (company_id, folder_id, file_name, original_name, file_path, 
                 file_size, file_type, mime_type, checksum, description, 
                 uploaded_by, uploaded_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                folder_id,
                unique_name,
                original_name,
                dest_path,
                file_size,
                file_ext,
                mime_type,
                checksum,
                description,
                uploaded_by,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ), company_id=company_id)

            # Etiketleri ekle
            if tags:
                for tag_name in tags:
                    tag_id = self._ensure_tag(tag_name, company_id)
                    # file_tag_relations now has company_id
                    self.execute_update("""
                        INSERT INTO file_tag_relations (file_id, tag_id, company_id, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (file_id, tag_id, company_id, datetime.now().isoformat()), company_id=company_id)

            # Metadata ekle
            if metadata:
                for key, value in metadata.items():
                    # file_metadata now has company_id
                    self.execute_update("""
                        INSERT INTO file_metadata (file_id, company_id, meta_key, meta_value)
                        VALUES (?, ?, ?, ?)
                    """, (file_id, company_id, key, value), company_id=company_id)

            return file_id

        except Exception as e:
            logging.error(f"Dosya yükleme hatası: {e}")
            return None

    def upload_multiple_files(self, company_id: int, file_paths: List[str],
                             folder_id: Optional[int] = None,
                             uploaded_by: Optional[int] = None) -> List[int]:
        """
        Birden fazla dosya yükle
        
        Args:
            company_id: Şirket ID
            file_paths: Dosya yolları listesi
            folder_id: Hedef klasör ID
            uploaded_by: Yükleyen kullanıcı ID
        
        Returns:
            Yüklenen dosya ID'leri listesi
        """
        file_ids = []
        for file_path in file_paths:
            file_id = self.upload_file(
                company_id=company_id,
                source_path=file_path,
                folder_id=folder_id,
                uploaded_by=uploaded_by
            )
            if file_id:
                file_ids.append(file_id)

        return file_ids

    def create_new_version(self, company_id: int, original_file_id: int, new_file_path: str,
                          uploaded_by: Optional[int] = None) -> Optional[int]:
        """
        Dosyanın yeni versiyonunu oluştur
        
        Args:
            company_id: Şirket ID
            original_file_id: Orijinal dosya ID
            new_file_path: Yeni dosya yolu
            uploaded_by: Yükleyen kullanıcı ID
        
        Returns:
            Yeni versiyon ID veya None
        """
        try:
            # Orijinal dosya bilgilerini al
            # Uses execute_query which enforces company_id context
            rows = self.execute_query("""
                SELECT company_id, folder_id, original_name, description, version
                FROM files
                WHERE id = ? AND is_deleted = 0
            """, (original_file_id,), company_id=company_id)

            if not rows:
                return None

            result = rows[0]
            # Verify company_id matches (redundant if filtered, but safe)
            if result['company_id'] != company_id:
                return None
                
            folder_id = result['folder_id']
            description = result['description']
            current_version = result['version']

            # Yeni versiyon numarası
            new_version = current_version + 1

            # Yeni versiyonu yükle
            file_id = self.upload_file(
                company_id=company_id,
                source_path=new_file_path,
                folder_id=folder_id,
                description=f"{description} (v{new_version})",
                uploaded_by=uploaded_by
            )

            if file_id:
                # Versiyon bilgisini güncelle
                self.execute_update("""
                    UPDATE files 
                    SET version = ?, parent_version_id = ?
                    WHERE id = ?
                """, (new_version, original_file_id, file_id), company_id=company_id)

            return file_id

        except Exception as e:
            logging.error(f"Versiyon oluşturma hatası: {e}")
            return None

    def get_file_versions(self, file_id: int, company_id: Optional[int] = None) -> List[Dict]:
        """
        Dosyanın tüm versiyonlarını al
        
        Args:
            file_id: Dosya ID
            company_id: Şirket ID (opsiyonel ama önerilen)
        
        Returns:
            Versiyon listesi
        """
        try:
            # Dosya ID'nin kök versiyonunu bul
            rows = self.execute_query("""
                SELECT COALESCE(parent_version_id, id) as root_id
                FROM files
                WHERE id = ?
            """, (file_id,), company_id=company_id)

            if not rows:
                return []

            root_id = rows[0]['root_id']

            # Tüm versiyonları getir
            version_rows = self.execute_query("""
                SELECT id, file_name, original_name, version, file_size, uploaded_at, uploaded_by
                FROM files
                WHERE (id = ? OR parent_version_id = ?) AND is_deleted = 0
                ORDER BY version ASC
            """, (root_id, root_id), company_id=company_id)

            versions = []
            for row in version_rows:
                versions.append({
                    'id': row['id'],
                    'file_name': row['file_name'],
                    'original_name': row['original_name'],
                    'version': row['version'],
                    'file_size': row['file_size'],
                    'uploaded_at': row['uploaded_at'],
                    'uploaded_by': row['uploaded_by']
                })

            return versions

        except Exception as e:
            logging.error(f"Versiyon listeleme hatası: {e}")
            return []

    def list_files(self, company_id: int, folder_id: Optional[int] = None,
                  tags: List[str] = None, search_term: str = "") -> List[Dict]:
        """
        Dosyaları listele
        
        Args:
            company_id: Şirket ID
            folder_id: Klasör ID filtresi
            tags: Etiket filtresi
            search_term: Arama terimi
        
        Returns:
            Dosya listesi
        """
        try:
            # Temel sorgu
            query = """
                SELECT DISTINCT f.id, f.original_name, f.file_size, f.file_type, 
                       f.description, f.uploaded_at, f.version,
                       (SELECT COUNT(*) FROM files WHERE parent_version_id = f.id OR 
                        (f.parent_version_id IS NOT NULL AND (parent_version_id = f.parent_version_id OR id = f.parent_version_id))) as version_count
                FROM files f
                WHERE f.company_id = ? AND f.is_deleted = 0
            """
            params = [company_id]

            # Klasör filtresi
            if folder_id is not None:
                query += " AND f.folder_id = ?"
                params.append(folder_id)

            # Etiket filtresi
            if tags:
                placeholders = ','.join('?' * len(tags))
                query += f"""
                    AND f.id IN (
                        SELECT file_id FROM file_tag_relations ftr
                        JOIN file_tags ft ON ftr.tag_id = ft.id
                        WHERE ft.tag_name IN ({placeholders})
                    )
                """
                params.extend(tags)

            # Arama
            if search_term:
                query += " AND (f.original_name LIKE ? OR f.description LIKE ?)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern])

            query += " ORDER BY f.uploaded_at DESC"

            # Use execute_query with company_id context
            # Note: We manually built the query with company_id filter, 
            # so we could pass company_id=None to avoid double injection, 
            # OR rely on BaseTenantManager to detect existing filter.
            # inject_tenant_filter checks "if 'company_id' in sql_lower".
            # Our query has "f.company_id = ?", so it should detect it and NOT inject another one.
            rows = self.execute_query(query, tuple(params), company_id=company_id)

            files = []
            for row in rows:
                # Etiketleri al
                # Direct DB access for tags (global)
                tag_rows = self.db.execute_query("""
                    SELECT ft.tag_name, ft.tag_color
                    FROM file_tag_relations ftr
                    JOIN file_tags ft ON ftr.tag_id = ft.id
                    WHERE ftr.file_id = ?
                """, (row['id'],))

                tags_list = [{'name': t['tag_name'], 'color': t['tag_color']} for t in tag_rows]

                files.append({
                    'id': row['id'],
                    'name': row['original_name'],
                    'size': row['file_size'],
                    'type': row['file_type'],
                    'description': row['description'],
                    'uploaded_at': row['uploaded_at'],
                    'version': row['version'],
                    'version_count': row['version_count'],
                    'tags': tags_list
                })

            return files

        except Exception as e:
            logging.error(f"Dosya listeleme hatası: {e}")
            return []

    def delete_file(self, file_id: int, company_id: Optional[int] = None) -> bool:
        """
        Dosyayı sil (soft delete)
        
        Args:
            file_id: Dosya ID
            company_id: Şirket ID (opsiyonel, güvenlik için önerilir)
        
        Returns:
            Başarılı ise True
        """
        try:
            # Soft delete
            # Use execute_update with company_id context
            self.execute_update("""
                UPDATE files 
                SET is_deleted = 1, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), file_id), company_id=company_id)

            return True

        except Exception as e:
            logging.error(f"Dosya silme hatası: {e}")
            return False

    # ============================================
    # ETİKET YÖNETİMİ
    # ============================================

    def _ensure_tag(self, tag_name: str, company_id: int) -> int:
        """Etiketin var olduğundan emin ol, yoksa oluştur"""
        # Using direct db access, but now filtering by company_id
        rows = self.db.execute_query("SELECT id FROM file_tags WHERE tag_name = ? AND company_id = ?", (tag_name, company_id))
        
        if rows:
            return rows[0]['id']
        else:
            tag_id = self.db.execute_update("""
                INSERT INTO file_tags (company_id, tag_name, created_at)
                VALUES (?, ?, ?)
            """, (company_id, tag_name, datetime.now().isoformat()))
            return tag_id

    def add_tags_to_file(self, file_id: int, tags: List[str], company_id: Optional[int] = None) -> bool:
        """
        Dosyaya etiket ekle
        
        Args:
            file_id: Dosya ID
            tags: Etiketler listesi
            company_id: Şirket ID (opsiyonel)
        
        Returns:
            Başarılı ise True
        """
        try:
            if not self._verify_file_ownership(file_id, company_id):
                logging.warning(f"Add Tags: File {file_id} not found or access denied")
                return False

            # If company_id is None (but ownership verified), we need the company_id from the file
            # to create tags for the correct company.
            if company_id is None:
                 rows = self.execute_query("SELECT company_id FROM files WHERE id = ?", (file_id,))
                 if not rows:
                     return False
                 company_id = rows[0]['company_id']

            for tag_name in tags:
                tag_id = self._ensure_tag(tag_name, company_id)

                # İlişkiyi ekle (varsa ignore et)
                self.db.execute_update("""
                    INSERT OR IGNORE INTO file_tag_relations (file_id, tag_id, company_id, created_at)
                    VALUES (?, ?, ?, ?)
                """, (file_id, tag_id, company_id, datetime.now().isoformat()))

            return True

        except Exception as e:
            logging.error(f"Etiket ekleme hatası: {e}")
            return False

    def remove_tags_from_file(self, file_id: int, tags: List[str], company_id: Optional[int] = None) -> bool:
        """
        Dosyadan etiket kaldır
        
        Args:
            file_id: Dosya ID
            tags: Kaldırılacak etiketler
            company_id: Şirket ID (opsiyonel)
        
        Returns:
            Başarılı ise True
        """
        try:
            if not self._verify_file_ownership(file_id, company_id):
                logging.warning(f"Remove Tags: File {file_id} not found or access denied")
                return False

            placeholders = ','.join('?' * len(tags))
            # Use direct execution as tags are global
            self.db.execute_update(f"""
                DELETE FROM file_tag_relations
                WHERE file_id = ? AND tag_id IN (
                    SELECT id FROM file_tags WHERE tag_name IN ({placeholders})
                )
            """, [file_id] + tags)

            return True

        except Exception as e:
            logging.error(f"Etiket kaldırma hatası: {e}")
            return False

    def get_all_tags(self, company_id: int) -> List[Dict]:
        """Tüm etiketleri listele"""
        try:
            # Use direct execution, filter by company_id
            rows = self.db.execute_query("""
                SELECT ft.id, ft.tag_name, ft.tag_color, COUNT(ftr.file_id) as usage_count
                FROM file_tags ft
                LEFT JOIN file_tag_relations ftr ON ft.id = ftr.tag_id
                WHERE ft.company_id = ?
                GROUP BY ft.id
                ORDER BY usage_count DESC, ft.tag_name
            """, (company_id,))

            tags = []
            for row in rows:
                tags.append({
                    'id': row['id'],
                    'name': row['tag_name'],
                    'color': row['tag_color'],
                    'usage_count': row['usage_count']
                })

            return tags

        except Exception as e:
            logging.error(f"Etiket listeleme hatası: {e}")
            return []

    # ============================================
    # METADATA YÖNETİMİ
    # ============================================

    def add_metadata(self, file_id: int, key: str, value: str, company_id: Optional[int] = None) -> bool:
        """Dosyaya metadata ekle"""
        try:
            if not self._verify_file_ownership(file_id, company_id):
                logging.warning(f"Add Metadata: File {file_id} not found or access denied")
                return False

            if company_id is None:
                rows = self.execute_query("SELECT company_id FROM files WHERE id = ?", (file_id,))
                if not rows:
                    return False
                company_id = rows[0]['company_id']

            # Direct execution for metadata
            self.db.execute_update("""
                INSERT INTO file_metadata (file_id, company_id, meta_key, meta_value)
                VALUES (?, ?, ?, ?)
            """, (file_id, company_id, key, value))

            return True

        except Exception as e:
            logging.error(f"Metadata ekleme hatası: {e}")
            return False

    def get_metadata(self, file_id: int, company_id: Optional[int] = None) -> Dict[str, str]:
        """Dosya metadata'sını al"""
        try:
            if not self._verify_file_ownership(file_id, company_id):
                logging.warning(f"Get Metadata: File {file_id} not found or access denied")
                return {}

            # Direct execution for metadata
            rows = self.db.execute_query("""
                SELECT meta_key, meta_value
                FROM file_metadata
                WHERE file_id = ?
            """, (file_id,))

            metadata = {row['meta_key']: row['meta_value'] for row in rows}

            return metadata

        except Exception as e:
            logging.error(f"Metadata alma hatası: {e}")
            return {}

    # ============================================
    # PAYLAŞIM YÖNETİMİ
    # ============================================

    def share_file(self, file_id: int, shared_with_user_id: Optional[int] = None,
                  shared_with_company_id: Optional[int] = None,
                  permission: str = 'view', shared_by: Optional[int] = None,
                  expires_at: Optional[str] = None, company_id: Optional[int] = None) -> bool:
        """Dosyayı paylaş"""
        try:
            # Verify ownership and get company_id
            rows = self.execute_query("SELECT company_id FROM files WHERE id = ?", (file_id,), company_id=company_id)
            if not rows:
                logging.warning(f"Share File: File {file_id} not found or access denied")
                return False
            
            file_company_id = rows[0]['company_id']

            # Direct execution for shares
            self.db.execute_update("""
                INSERT INTO file_shares 
                (file_id, company_id, shared_with_user_id, shared_with_company_id, permission, shared_by, shared_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id,
                file_company_id,
                shared_with_user_id,
                shared_with_company_id,
                permission,
                shared_by,
                datetime.now().isoformat(),
                expires_at
            ))

            return True

        except Exception as e:
            logging.error(f"Dosya paylaşma hatası: {e}")
            return False

    def get_file_info(self, file_id: int, company_id: Optional[int] = None) -> Optional[Dict]:
        """Dosya bilgilerini al"""
        try:
            # Uses execute_query which enforces company_id context
            rows = self.execute_query("""
                SELECT id, original_name, file_path, file_size, file_type, 
                       description, version, uploaded_at, checksum
                FROM files
                WHERE id = ? AND is_deleted = 0
            """, (file_id,), company_id=company_id)

            if not rows:
                return None

            result = rows[0]
            file_info = {
                'id': result['id'],
                'name': result['original_name'],
                'path': result['file_path'],
                'size': result['file_size'],
                'type': result['file_type'],
                'description': result['description'],
                'version': result['version'],
                'uploaded_at': result['uploaded_at'],
                'checksum': result['checksum']
            }

            return file_info

        except Exception as e:
            logging.error(f"Dosya bilgisi alma hatası: {e}")
            return None

