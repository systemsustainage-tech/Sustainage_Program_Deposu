import sqlite3
import logging
from typing import List, Dict, Optional, Any
from config.database import DB_PATH

class LCAManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_products(self, company_id: int) -> List[Dict]:
        """Şirkete ait ürünleri listeler."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lca_products WHERE company_id = ? ORDER BY created_at DESC", (company_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def add_product(self, company_id: int, name: str, description: str, unit: str) -> int:
        """Yeni ürün ekler."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lca_products (company_id, name, description, unit)
                VALUES (?, ?, ?, ?)
            """, (company_id, name, description, unit))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_assessments(self, product_id: int, company_id: int) -> List[Dict]:
        """Bir ürüne ait analizleri listeler."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM lca_assessments 
                WHERE product_id = ? AND company_id = ? 
                ORDER BY created_at DESC
            """, (product_id, company_id))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def add_assessment(self, product_id: int, company_id: int, name: str, assessment_date: str) -> int:
        """Yeni analiz (senaryo) ekler."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lca_assessments (product_id, company_id, name, assessment_date)
                VALUES (?, ?, ?, ?)
            """, (product_id, company_id, name, assessment_date))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
            
    def get_assessment_details(self, assessment_id: int, company_id: int) -> Optional[Dict]:
        """Analiz detayını getirir."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, p.name as product_name, p.unit as product_unit 
                FROM lca_assessments a
                JOIN lca_products p ON a.product_id = p.id
                WHERE a.id = ? AND a.company_id = ?
            """, (assessment_id, company_id))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_entries(self, assessment_id: int, company_id: int) -> List[Dict]:
        """Analiz verilerini listeler."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM lca_entries 
                WHERE assessment_id = ? AND company_id = ?
                ORDER BY stage, id
            """, (assessment_id, company_id))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def add_entry(self, assessment_id: int, company_id: int, data: Dict) -> int:
        """Analize veri ekler."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lca_entries (
                    assessment_id, company_id, stage, item_name, quantity, unit, 
                    co2e_factor, energy_consumption, water_consumption, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment_id, company_id, data['stage'], data['item_name'], 
                data.get('quantity', 0), data.get('unit', ''), 
                data.get('co2e_factor', 0), data.get('energy_consumption', 0), 
                data.get('water_consumption', 0), data.get('notes', '')
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
            
    def delete_entry(self, entry_id: int, company_id: int):
        """Veri siler."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lca_entries WHERE id = ? AND company_id = ?", (entry_id, company_id))
            conn.commit()
        finally:
            conn.close()

    def calculate_results(self, assessment_id: int, company_id: int) -> Dict:
        """Analiz sonuçlarını hesaplar."""
        entries = self.get_entries(assessment_id, company_id)
        
        stages = ['raw_material', 'production', 'distribution', 'use', 'end_of_life']
        results = {stage: {'co2e': 0, 'energy': 0, 'water': 0} for stage in stages}
        total = {'co2e': 0, 'energy': 0, 'water': 0}
        
        for entry in entries:
            stage = entry['stage']
            qty = entry['quantity'] or 0
            
            # Calculations
            co2e = qty * (entry['co2e_factor'] or 0)
            energy = entry['energy_consumption'] or 0 # Assuming input is total or per unit? 
            # Usually input is per unit for factors, but here fields are "energy_consumption". 
            # Let's assume user enters TOTAL energy for that line item, OR we treat it as factor?
            # Looking at table: "energy_consumption REAL". 
            # Let's treat energy/water as TOTAL for that entry for simplicity in UI, 
            # OR we can treat them as per unit. 
            # Let's assume they are TOTAL values entered by user, OR factors.
            # Standard LCA tools have quantity * factor. 
            # My table has co2e_factor. But energy/water are just "consumption". 
            # Let's assume they are absolute values for this entry.
            
            # Wait, if I have electricity: 100 kWh. CO2 factor: 0.5 kg/kWh. 
            # Energy consumption IS the quantity (100 kWh).
            # But if I have Steel: 10 kg. Energy to produce: 5 kWh/kg.
            # Let's keep it simple: The user enters the calculated impact OR the system calculates CO2.
            # Table says: quantity, unit, co2e_factor. 
            # Calculated CO2 = quantity * co2e_factor.
            # Energy/Water: Let's assume these are direct inputs for that line item (Total).
            
            water = entry['water_consumption'] or 0
            
            if stage in results:
                results[stage]['co2e'] += co2e
                results[stage]['energy'] += energy
                results[stage]['water'] += water
                
                total['co2e'] += co2e
                total['energy'] += energy
                total['water'] += water
                
        return {'by_stage': results, 'total': total}
