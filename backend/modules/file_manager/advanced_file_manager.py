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
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class AdvancedFileManager:
    """Gelişmiş dosya yönetimi sınıfı"""

    def __init__(self, db_path: str, base_upload_dir: str = None) -> None:
        """
        Args:
            db_path: Veritabanı yolu
            base_upload_dir: Dosya yükleme klasörü
        """
        self.db_path = db_path
        if base_upload_dir:
             self.base_upload_dir = base_upload_dir
        else:
             # Default to uploads folder in project root
             root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
             self.base_upload_dir = os.path.join(root_dir, 'uploads')
             
        self._init_database()
        self._ensure_upload_directory()

    def _init_database(self) -> None:
        """Veritabanı tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Dosyalar tablosu
        cursor.execute("""
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
        cursor.execute("""
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE NOT NULL,
                tag_color TEXT DEFAULT '#3498db',
                created_at TEXT
            )
        """)

        # Dosya-etiket ilişkileri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_tag_relations (
                file_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at TEXT,
                PRIMARY KEY (file_id, tag_id),
                FOREIGN KEY (file_id) REFERENCES files(id),
                FOREIGN KEY (tag_id) REFERENCES file_tags(id)
            )
        """)

        # Dosya metadata tablosu (ek bilgiler için)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                meta_key TEXT NOT NULL,
                meta_value TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id)
            )
        """)

        # Dosya paylaşım tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                shared_with_user_id INTEGER,
                shared_with_company_id INTEGER,
                permission TEXT DEFAULT 'view',
                shared_by INTEGER,
                shared_at TEXT,
                expires_at TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id)
            )
        """)

        # İndeksler
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_company 
            ON files(company_id, is_deleted)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_folder 
            ON files(folder_id, is_deleted)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_version 
            ON files(parent_version_id)
        """)

        conn.commit()
        conn.close()

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
                folder_path = os.path.join(parent_path, folder_name)
            else:
                folder_path = os.path.join(
                    self.base_upload_dir,
                    f"company_{company_id}",
                    folder_name
                )

            # Fiziksel klasörü oluştur
            os.makedirs(folder_path, exist_ok=True)

            # Veritabanına kaydet
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
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
            ))

            folder_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return folder_id

        except Exception as e:
            logging.error(f"Klasör oluşturma hatası: {e}")
            return None

    def get_folder_path(self, folder_id: int) -> Optional[str]:
        """Klasör yolunu al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT folder_path FROM file_folders WHERE id = ?", (folder_id,))
            result = cursor.fetchone()
            conn.close()

            return result[0] if result else None

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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if parent_folder_id is None:
                cursor.execute("""
                    SELECT id, folder_name, description, created_at, 
                           (SELECT COUNT(*) FROM files WHERE folder_id = file_folders.id AND is_deleted = 0) as file_count
                    FROM file_folders
                    WHERE company_id = ? AND parent_folder_id IS NULL AND is_deleted = 0
                    ORDER BY folder_name
                """, (company_id,))
            else:
                cursor.execute("""
                    SELECT id, folder_name, description, created_at,
                           (SELECT COUNT(*) FROM files WHERE folder_id = file_folders.id AND is_deleted = 0) as file_count
                    FROM file_folders
                    WHERE company_id = ? AND parent_folder_id = ? AND is_deleted = 0
                    ORDER BY folder_name
                """, (company_id, parent_folder_id))

            folders = []
            for row in cursor.fetchall():
                folders.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'created_at': row[3],
                    'file_count': row[4]
                })

            conn.close()
            return folders

        except Exception as e:
            logging.error(f"Klasör listeleme hatası: {e}")
            return []

    def delete_folder(self, folder_id: int) -> bool:
        """
        Klasörü sil (soft delete)
        
        Args:
            folder_id: Klasör ID
        
        Returns:
            Başarılı ise True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Soft delete
            cursor.execute("""
                UPDATE file_folders 
                SET is_deleted = 1, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), folder_id))

            # İçindeki dosyaları da sil
            cursor.execute("""
                UPDATE files 
                SET is_deleted = 1, updated_at = ?
                WHERE folder_id = ?
            """, (datetime.now().isoformat(), folder_id))

            conn.commit()
            conn.close()
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
                folder_path = self.get_folder_path(folder_id)
                if not folder_path:
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
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
            ))

            file_id = cursor.lastrowid

            # Etiketleri ekle
            if tags:
                for tag_name in tags:
                    tag_id = self._ensure_tag(cursor, tag_name)
                    cursor.execute("""
                        INSERT INTO file_tag_relations (file_id, tag_id, created_at)
                        VALUES (?, ?, ?)
                    """, (file_id, tag_id, datetime.now().isoformat()))

            # Metadata ekle
            if metadata:
                for key, value in metadata.items():
                    cursor.execute("""
                        INSERT INTO file_metadata (file_id, meta_key, meta_value)
                        VALUES (?, ?, ?)
                    """, (file_id, key, value))

            conn.commit()
            conn.close()

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

    def create_new_version(self, original_file_id: int, new_file_path: str,
                          uploaded_by: Optional[int] = None) -> Optional[int]:
        """
        Dosyanın yeni versiyonunu oluştur
        
        Args:
            original_file_id: Orijinal dosya ID
            new_file_path: Yeni dosya yolu
            uploaded_by: Yükleyen kullanıcı ID
        
        Returns:
            Yeni versiyon ID veya None
        """
        try:
            # Orijinal dosya bilgilerini al
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT company_id, folder_id, original_name, description, version
                FROM files
                WHERE id = ? AND is_deleted = 0
            """, (original_file_id,))

            result = cursor.fetchone()
            if not result:
                conn.close()
                return None

            company_id, folder_id, original_name, description, current_version = result
            conn.close()

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
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE files 
                    SET version = ?, parent_version_id = ?
                    WHERE id = ?
                """, (new_version, original_file_id, file_id))

                conn.commit()
                conn.close()

            return file_id

        except Exception as e:
            logging.error(f"Versiyon oluşturma hatası: {e}")
            return None

    def get_file_versions(self, file_id: int) -> List[Dict]:
        """
        Dosyanın tüm versiyonlarını al
        
        Args:
            file_id: Dosya ID
        
        Returns:
            Versiyon listesi
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Dosya ID'nin kök versiyonunu bul
            cursor.execute("""
                SELECT COALESCE(parent_version_id, id) as root_id
                FROM files
                WHERE id = ?
            """, (file_id,))

            result = cursor.fetchone()
            if not result:
                conn.close()
                return []

            root_id = result[0]

            # Tüm versiyonları getir
            cursor.execute("""
                SELECT id, file_name, original_name, version, file_size, uploaded_at, uploaded_by
                FROM files
                WHERE (id = ? OR parent_version_id = ?) AND is_deleted = 0
                ORDER BY version ASC
            """, (root_id, root_id))

            versions = []
            for row in cursor.fetchall():
                versions.append({
                    'id': row[0],
                    'file_name': row[1],
                    'original_name': row[2],
                    'version': row[3],
                    'file_size': row[4],
                    'uploaded_at': row[5],
                    'uploaded_by': row[6]
                })

            conn.close()
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

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

            cursor.execute(query, params)

            files = []
            for row in cursor.fetchall():
                # Etiketleri al
                cursor.execute("""
                    SELECT ft.tag_name, ft.tag_color
                    FROM file_tag_relations ftr
                    JOIN file_tags ft ON ftr.tag_id = ft.id
                    WHERE ftr.file_id = ?
                """, (row[0],))

                tags_list = [{'name': t[0], 'color': t[1]} for t in cursor.fetchall()]

                files.append({
                    'id': row[0],
                    'name': row[1],
                    'size': row[2],
                    'type': row[3],
                    'description': row[4],
                    'uploaded_at': row[5],
                    'version': row[6],
                    'version_count': row[7],
                    'tags': tags_list
                })

            conn.close()
            return files

        except Exception as e:
            logging.error(f"Dosya listeleme hatası: {e}")
            return []

    def delete_file(self, file_id: int) -> bool:
        """
        Dosyayı sil (soft delete)
        
        Args:
            file_id: Dosya ID
        
        Returns:
            Başarılı ise True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE files 
                SET is_deleted = 1, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), file_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Dosya silme hatası: {e}")
            return False

    # ============================================
    # ETİKET YÖNETİMİ
    # ============================================

    def _ensure_tag(self, cursor, tag_name: str) -> int:
        """Etiketin var olduğundan emin ol, yoksa oluştur"""
        cursor.execute("SELECT id FROM file_tags WHERE tag_name = ?", (tag_name,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            cursor.execute("""
                INSERT INTO file_tags (tag_name, created_at)
                VALUES (?, ?)
            """, (tag_name, datetime.now().isoformat()))
            return cursor.lastrowid

    def add_tags_to_file(self, file_id: int, tags: List[str]) -> bool:
        """
        Dosyaya etiket ekle
        
        Args:
            file_id: Dosya ID
            tags: Etiketler listesi
        
        Returns:
            Başarılı ise True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for tag_name in tags:
                tag_id = self._ensure_tag(cursor, tag_name)

                # İlişkiyi ekle (varsa ignore et)
                cursor.execute("""
                    INSERT OR IGNORE INTO file_tag_relations (file_id, tag_id, created_at)
                    VALUES (?, ?, ?)
                """, (file_id, tag_id, datetime.now().isoformat()))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Etiket ekleme hatası: {e}")
            return False

    def remove_tags_from_file(self, file_id: int, tags: List[str]) -> bool:
        """
        Dosyadan etiket kaldır
        
        Args:
            file_id: Dosya ID
            tags: Kaldırılacak etiketler
        
        Returns:
            Başarılı ise True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(tags))
            cursor.execute(f"""
                DELETE FROM file_tag_relations
                WHERE file_id = ? AND tag_id IN (
                    SELECT id FROM file_tags WHERE tag_name IN ({placeholders})
                )
            """, [file_id] + tags)

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Etiket kaldırma hatası: {e}")
            return False

    def get_all_tags(self) -> List[Dict]:
        """Tüm etiketleri listele"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ft.id, ft.tag_name, ft.tag_color, COUNT(ftr.file_id) as usage_count
                FROM file_tags ft
                LEFT JOIN file_tag_relations ftr ON ft.id = ftr.tag_id
                GROUP BY ft.id
                ORDER BY usage_count DESC, ft.tag_name
            """)

            tags = []
            for row in cursor.fetchall():
                tags.append({
                    'id': row[0],
                    'name': row[1],
                    'color': row[2],
                    'usage_count': row[3]
                })

            conn.close()
            return tags

        except Exception as e:
            logging.error(f"Etiket listeleme hatası: {e}")
            return []

    # ============================================
    # METADATA YÖNETİMİ
    # ============================================

    def add_metadata(self, file_id: int, key: str, value: str) -> bool:
        """Dosyaya metadata ekle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO file_metadata (file_id, meta_key, meta_value)
                VALUES (?, ?, ?)
            """, (file_id, key, value))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Metadata ekleme hatası: {e}")
            return False

    def get_metadata(self, file_id: int) -> Dict[str, str]:
        """Dosya metadata'sını al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT meta_key, meta_value
                FROM file_metadata
                WHERE file_id = ?
            """, (file_id,))

            metadata = {row[0]: row[1] for row in cursor.fetchall()}

            conn.close()
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
                  expires_at: Optional[str] = None) -> bool:
        """Dosyayı paylaş"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO file_shares 
                (file_id, shared_with_user_id, shared_with_company_id, permission, shared_by, shared_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id,
                shared_with_user_id,
                shared_with_company_id,
                permission,
                shared_by,
                datetime.now().isoformat(),
                expires_at
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Dosya paylaşma hatası: {e}")
            return False

    def get_file_info(self, file_id: int) -> Optional[Dict]:
        """Dosya bilgilerini al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, original_name, file_path, file_size, file_type, 
                       description, version, uploaded_at, checksum
                FROM files
                WHERE id = ? AND is_deleted = 0
            """, (file_id,))

            result = cursor.fetchone()
            if not result:
                conn.close()
                return None

            file_info = {
                'id': result[0],
                'name': result[1],
                'path': result[2],
                'size': result[3],
                'type': result[4],
                'description': result[5],
                'version': result[6],
                'uploaded_at': result[7],
                'checksum': result[8]
            }

            conn.close()
            return file_info

        except Exception as e:
            logging.error(f"Dosya bilgisi alma hatası: {e}")
            return None

