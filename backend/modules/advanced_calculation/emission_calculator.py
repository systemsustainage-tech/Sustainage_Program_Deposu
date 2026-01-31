#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gelismis Hesaplama - Emisyon, Karbon"""

class EmissionCalculator:
    """Emisyon hesaplama yoneticisi"""

    def __init__(self):
        # Varsayılan emisyon faktörleri (kg CO2e / birim)
        self.factors = {
            # Yakıtlar (kg CO2e / litre veya kg)
            'diesel': 2.68,
            'petrol': 2.31,
            'natural_gas': 1.9, # m3 başına
            'coal': 2.4,
            
            # Elektrik (kg CO2e / kWh) - Türkiye ortalaması (örnek)
            'electricity_tr': 0.44,
            
            # Kargo/Ulaşım (kg CO2e / km-ton)
            'transport_road': 0.062,
            'transport_air': 0.602,
            'transport_sea': 0.01
        }

    def calculate_scope1(self, fuel_data: list) -> dict:
        """
        Scope 1 (Doğrudan) emisyon hesapla
        fuel_data: [{'type': 'diesel', 'amount': 100}, ...]
        """
        total_co2 = 0
        for item in fuel_data:
            fuel_type = item.get('type')
            amount = float(item.get('amount', 0))
            factor = self.factors.get(fuel_type, 0)
            total_co2 += amount * factor
            
        return {
            "co2": round(total_co2, 2),
            "ch4": 0, # Şimdilik ihmal
            "n2o": 0, # Şimdilik ihmal
            "total": round(total_co2, 2)
        }

    def calculate_scope2(self, electricity_data: dict) -> dict:
        """
        Scope 2 (Enerji Dolaylı) emisyon hesapla
        electricity_data: {'consumption_kwh': 1000, 'source': 'grid'}
        """
        consumption = float(electricity_data.get('consumption_kwh', 0))
        # Market-based (tedarikçi özelinde) vs Location-based (şebeke ortalaması)
        # Şimdilik sadece TR şebeke ortalamasını kullanıyoruz
        factor = self.factors.get('electricity_tr', 0.44)
        
        emission = consumption * factor
        
        return {
            "market_based": round(emission, 2), # Yenilenebilir sertifikası varsa 0 olabilir
            "location_based": round(emission, 2)
        }

    def calculate_scope3(self, activity_data: list) -> dict:
        """
        Scope 3 (Diğer Dolaylı) emisyon hesapla
        activity_data: [{'category': 'transport_road', 'amount': 500}, ...]
        """
        total = 0
        categories = {}
        
        for item in activity_data:
            category = item.get('category')
            amount = float(item.get('amount', 0))
            factor = self.factors.get(category, 0)
            emission = amount * factor
            
            total += emission
            categories[category] = categories.get(category, 0) + emission
            
        return {
            "total": round(total, 2),
            "categories": {k: round(v, 2) for k, v in categories.items()}
        }

    def calculate_carbon_footprint(self, company_id, year) -> dict:
        """
        Karbon ayak izi hesapla (Veritabanından veri çekme mantığı buraya eklenebilir)
        Şimdilik manuel parametrelerle çağrılacak şekilde tasarlandı.
        """
        # Not: Bu metodun veritabanı bağlantısı olmadığı için
        # şimdilik 0 dönüyor, ancak üstteki metodlar kullanılabilir.
        return {
            "total_co2e": 0,
            "by_scope": {
                "scope1": 0,
                "scope2": 0,
                "scope3": 0
            }
        }

