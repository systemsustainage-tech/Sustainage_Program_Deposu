import logging
from typing import List, Dict, Optional, Any
from backend.core.base_manager import BaseTenantManager
try:
    from config.database import DB_PATH
except ImportError:
    from backend.config.database import DB_PATH

class LCAManager(BaseTenantManager):
    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        self.logger = logging.getLogger(__name__)

    def get_products(self, company_id: int) -> List[Dict]:
        """Şirkete ait ürünleri listeler."""
        sql = "SELECT * FROM lca_products WHERE company_id = ? ORDER BY created_at DESC"
        rows = self.execute_query(sql, (company_id,), company_id=company_id)
        return [dict(row) for row in rows]

    def add_product(self, company_id: int, name: str, description: str, unit: str) -> int:
        """Yeni ürün ekler."""
        sql = """
            INSERT INTO lca_products (company_id, name, description, unit)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_update(sql, (company_id, name, description, unit), company_id=company_id)

    def get_assessments(self, product_id: int, company_id: int) -> List[Dict]:
        """Bir ürüne ait analizleri listeler."""
        sql = """
            SELECT * FROM lca_assessments 
            WHERE product_id = ? AND company_id = ? 
            ORDER BY created_at DESC
        """
        rows = self.execute_query(sql, (product_id, company_id), company_id=company_id)
        return [dict(row) for row in rows]

    def add_assessment(self, product_id: int, company_id: int, name: str, assessment_date: str) -> int:
        """Yeni analiz (senaryo) ekler."""
        sql = """
            INSERT INTO lca_assessments (product_id, company_id, name, assessment_date)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_update(sql, (product_id, company_id, name, assessment_date), company_id=company_id)
            
    def get_assessment_details(self, assessment_id: int, company_id: int) -> Optional[Dict]:
        """Analiz detayını getirir."""
        sql = """
            SELECT a.*, p.name as product_name, p.unit as product_unit 
            FROM lca_assessments a
            JOIN lca_products p ON a.product_id = p.id
            WHERE a.id = ? AND a.company_id = ?
        """
        rows = self.execute_query(sql, (assessment_id, company_id), company_id=company_id)
        return dict(rows[0]) if rows else None

    def get_entries(self, assessment_id: int, company_id: int) -> List[Dict]:
        """Analiz verilerini listeler."""
        sql = """
            SELECT * FROM lca_entries 
            WHERE assessment_id = ? AND company_id = ?
            ORDER BY stage, id
        """
        rows = self.execute_query(sql, (assessment_id, company_id), company_id=company_id)
        return [dict(row) for row in rows]

    def add_entry(self, assessment_id: int, company_id: int, data: Dict) -> int:
        """Analize veri ekler."""
        sql = """
            INSERT INTO lca_entries (
                assessment_id, company_id, stage, item_name, quantity, unit, 
                co2e_factor, energy_consumption, water_consumption, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(sql, (
            assessment_id, company_id, data['stage'], data['item_name'], 
            data.get('quantity', 0), data.get('unit', ''), 
            data.get('co2e_factor', 0), data.get('energy_consumption', 0), 
            data.get('water_consumption', 0), data.get('notes', '')
        ), company_id=company_id)
            
    def delete_entry(self, entry_id: int, company_id: int):
        """Veri siler."""
        self.execute_update("DELETE FROM lca_entries WHERE id = ? AND company_id = ?", (entry_id, company_id), company_id=company_id)


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
