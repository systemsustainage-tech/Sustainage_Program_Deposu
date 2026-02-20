#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Inventory Manager
Tracks inventory items, quantities, and categories with tenant isolation.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from backend.core.base_manager import BaseTenantManager
from config.database import DB_PATH

class InventoryManager(BaseTenantManager):
    """
    Gelişmiş Envanter Yöneticisi
    Stok takibi, kategori yönetimi ve envanter raporlaması sağlar.
    """

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._init_inventory_tables()

    def _init_inventory_tables(self) -> None:
        """Envanter tablolarını oluşturur"""
        try:
            # Envanter kalemleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS inventory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT,
                    quantity REAL DEFAULT 0,
                    unit TEXT DEFAULT 'adet',
                    min_stock_level REAL DEFAULT 0,
                    location TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Envanter hareketleri (Giriş/Çıkış)
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS inventory_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL, -- 'IN', 'OUT', 'ADJUSTMENT'
                    quantity REAL NOT NULL,
                    unit_price REAL,
                    total_price REAL,
                    notes TEXT,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (item_id) REFERENCES inventory_items(id)
                )
            """)
        except Exception as e:
            logging.error(f"Envanter tabloları oluşturulamadı: {e}")

    def add_item(self, company_id: int, name: str, category: str, 
                 quantity: float, unit: str, min_stock: float = 0, 
                 location: str = "", description: str = "") -> Optional[int]:
        """Yeni envanter kalemi ekle"""
        try:
            query = """
                INSERT INTO inventory_items 
                (company_id, name, category, quantity, unit, min_stock_level, location, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (company_id, name, category, quantity, unit, min_stock, location, description)
            return self.execute_update(query, params, company_id=company_id)
        except Exception as e:
            logging.error(f"Envanter ekleme hatası: {e}")
            return None

    def get_inventory(self, company_id: int, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Envanter listesini getir"""
        try:
            query = "SELECT * FROM inventory_items WHERE company_id = ?"
            params = [company_id]
            
            if category:
                query += " AND category = ?"
                params.append(category)
                
            query += " ORDER BY name"
            
            rows = self.execute_query(query, params, company_id=company_id)
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Envanter listeleme hatası: {e}")
            return []

    def update_stock(self, company_id: int, item_id: int, 
                     change_amount: float, transaction_type: str, 
                     notes: str = "") -> bool:
        """Stok güncelleme ve hareket kaydı"""
        try:
            # Mevcut stok kontrolü
            item = self.get_item(company_id, item_id)
            if not item:
                return False

            new_quantity = item['quantity'] + change_amount
            if new_quantity < 0:
                logging.warning(f"Stok yetersiz: {item['name']}")
                return False

            # Stok güncelle
            self.execute_update(
                "UPDATE inventory_items SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_quantity, item_id),
                company_id=company_id
            )

            # Hareket kaydı
            self.execute_update("""
                INSERT INTO inventory_transactions 
                (company_id, item_id, transaction_type, quantity, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, item_id, transaction_type, abs(change_amount), notes), company_id=company_id)

            return True
        except Exception as e:
            logging.error(f"Stok güncelleme hatası: {e}")
            return False

    def get_item(self, company_id: int, item_id: int) -> Optional[Dict[str, Any]]:
        """Tek bir envanter kalemini getir"""
        try:
            rows = self.execute_query(
                "SELECT * FROM inventory_items WHERE id = ? AND company_id = ?",
                (item_id, company_id),
                company_id=company_id
            )
            return dict(rows[0]) if rows else None
        except Exception as e:
            logging.error(f"Envanter kalemi getirme hatası: {e}")
            return None
