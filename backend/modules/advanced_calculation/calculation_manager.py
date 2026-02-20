#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Calculation Manager
Wraps EmissionCalculator and provides tenant-aware database operations.
"""

import logging
from typing import Optional, Dict, Any
from backend.core.base_manager import BaseTenantManager
from backend.modules.advanced_calculation.emission_calculator import EmissionCalculator
from config.database import DB_PATH

class CalculationManager(BaseTenantManager):
    """
    Gelişmiş Hesaplama Yöneticisi
    Emisyon hesaplamalarını ve sonuçlarını yönetir.
    """

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self.calculator = EmissionCalculator()
        self._init_calculation_tables()

    def _init_calculation_tables(self) -> None:
        """Hesaplama sonuçları için tabloları oluşturur"""
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS calculation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    calculation_type TEXT NOT NULL, -- 'scope1', 'scope2', 'scope3'
                    input_data TEXT, -- JSON formatında girdi verileri
                    result_data TEXT, -- JSON formatında sonuçlar
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
        except Exception as e:
            logging.error(f"Hesaplama tabloları oluşturulamadı: {e}")

    def calculate_and_save(self, company_id: int, calculation_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hesaplama yap ve sonucu kaydet"""
        import json
        
        result = {}
        if calculation_type == 'scope1':
            # input_data list formatında bekleniyor: [{'type': 'diesel', 'amount': 100}]
            if isinstance(input_data, list):
                result = self.calculator.calculate_scope1(input_data)
            else:
                # Tekil obje geldiyse listeye çevir
                result = self.calculator.calculate_scope1([input_data])
                
        elif calculation_type == 'scope2':
            result = self.calculator.calculate_scope2(input_data)
            
        elif calculation_type == 'scope3':
            if isinstance(input_data, list):
                result = self.calculator.calculate_scope3(input_data)
            else:
                result = self.calculator.calculate_scope3([input_data])
        
        # Sonucu kaydet
        try:
            self.execute_update("""
                INSERT INTO calculation_results (company_id, calculation_type, input_data, result_data)
                VALUES (?, ?, ?, ?)
            """, (company_id, calculation_type, json.dumps(input_data), json.dumps(result)), company_id=company_id)
        except Exception as e:
            logging.error(f"Hesaplama sonucu kaydedilemedi: {e}")
            
        return result
