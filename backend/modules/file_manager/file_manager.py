#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dosya Yönetim Sistemi
Dosya yükleme, saklama ve erişim işlemlerini yönetir.
"""

import logging
import hashlib
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from config.database import DB_PATH
from backend.core.base_manager import BaseTenantManager


class FileManager(BaseTenantManager):
    """
    Dosya yönetim sınıfı
    
    Görevlere ait dosyaların yüklenmesi, saklanması ve yönetiminden sorumludur.
    """

    def __init__(self, db_path: str = DB_PATH, upload_dir: str = "data/uploads", company_id: Optional[int] = None) -> None:
        """
        FileManager başlat
        
        Args:
            db_path: Veritabanı yolu
            upload_dir: Dosya yükleme dizini
            company_id: Şirket ID (opsiyonel)
        """
        super().__init__(db_path, company_id)
        self.upload_dir = upload_dir

        # Upload dizinini oluştur
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(os.path.join(upload_dir, 'tasks'), exist_ok=True)
        self._create_tables()

    def _create_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS task_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                uploaded_by INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """, skip_tenant_filter=True)

    def upload_file(
        self,
        company_id: int,
        source_path: str,
        task_id: int,
        uploaded_by: int,
        description: Optional[str] = None
    ) -> Optional[int]:
        """
        Dosya yükle
        
        Args:
            company_id: Şirket ID
            source_path: Kaynak dosya yolu
            task_id: İlgili görev ID
            uploaded_by: Yükleyen kullanıcı ID
            description: Dosya açıklaması
        
        Returns:
            Optional[int]: Yüklenen dosyanın ID'si veya None
        """
        try:
            # Dosya var mı kontrol et
            if not os.path.exists(source_path):
                logging.error(f"[HATA] Dosya bulunamadı: {source_path}")
                return None

            # Dosya boyutu kontrolü (max 10MB)
            file_size = os.path.getsize(source_path)
            max_size = 10 * 1024 * 1024  # 10MB

            if file_size > max_size:
                logging.error(f"[HATA] Dosya çok büyük: {file_size / 1024 / 1024:.2f} MB (Max: 10 MB)")
                return None

            # Dosya adı ve uzantısı
            file_name = os.path.basename(source_path)
            file_ext = os.path.splitext(file_name)[1].lower()

            # İzin verilen uzantılar
            allowed_extensions = ['.pdf', '.xlsx', '.xls', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.txt', '.csv']

            if file_ext not in allowed_extensions:
                logging.error(f"[HATA] İzin verilmeyen dosya tipi: {file_ext}")
                return None

            # Güvenli dosya adı oluştur (timestamp + SHA-256 hash)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_hash = hashlib.sha256(file_name.encode()).hexdigest()[:8]
            safe_name = f"{timestamp}_{file_hash}_{file_name}"

            # Hedef dizin (görev bazlı)
            task_dir = os.path.join(self.upload_dir, 'tasks', str(task_id))
            os.makedirs(task_dir, exist_ok=True)

            # Hedef yol
            dest_path = os.path.join(task_dir, safe_name)

            # Dosyayı kopyala
            shutil.copy2(source_path, dest_path)

            # Veritabanına kaydet
            return self.execute_update("""
                INSERT INTO task_attachments (
                    company_id, task_id, file_name, file_path, file_size, uploaded_by
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, task_id, file_name, dest_path, file_size, uploaded_by), company_id=company_id)

        except Exception as e:
            logging.error(f"[HATA] Dosya yükleme hatası: {e}")
            return None

    def get_task_files(self, company_id: int, task_id: int) -> List[Dict]:
        """
        Görevin dosyalarını getir
        
        Args:
            company_id: Şirket ID
            task_id: Görev ID
        
        Returns:
            List[Dict]: Dosya listesi
        """
        try:
            return self.execute_query("""
                SELECT 
                    ta.*,
                    u.username as uploaded_by_name
                FROM task_attachments ta
                LEFT JOIN users u ON ta.uploaded_by = u.id
                WHERE ta.task_id = ?
                ORDER BY ta.uploaded_at DESC
            """, (task_id,), company_id=company_id)

        except Exception as e:
            logging.error(f"[HATA] Dosya listeleme hatası: {e}")
            return []

    def delete_file(self, company_id: int, file_id: int) -> bool:
        """
        Dosyayı sil
        
        Args:
            company_id: Şirket ID
            file_id: Dosya ID
        
        Returns:
            bool: Başarılı mı?
        """
        try:
            # Dosya bilgisini al
            result = self.execute_query("SELECT file_path FROM task_attachments WHERE id = ?", (file_id,), company_id=company_id)

            if not result:
                return False

            file_path = result[0]['file_path']

            # Fiziksel dosyayı sil
            if os.path.exists(file_path):
                os.remove(file_path)

            # Veritabanından sil
            self.execute_update("DELETE FROM task_attachments WHERE id = ?", (file_id,), company_id=company_id)

            logging.info(f"[OK] Dosya silindi: #{file_id}")
            return True

        except Exception as e:
            logging.error(f"[HATA] Dosya silme hatası: {e}")
            return False

    def get_file_path(self, company_id: int, file_id: int) -> Optional[str]:
        """
        Dosya yolunu getir
        
        Args:
            company_id: Şirket ID
            file_id: Dosya ID
        
        Returns:
            Optional[str]: Dosya yolu veya None
        """
        try:
            result = self.execute_query("SELECT file_path FROM task_attachments WHERE id = ?", (file_id,), company_id=company_id)

            if result:
                return result[0]['file_path']
            return None

        except Exception as e:
            logging.error(f"[HATA] Dosya yolu getirme hatası: {e}")
            return None

