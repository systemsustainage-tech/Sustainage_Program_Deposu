# -*- coding: utf-8 -*-
"""
Uluslararası Emisyon Faktörleri Kütüphanesi Veri Seti
Kaynaklar: DEFRA (UK Government GHG Conversion Factors), IPCC, EPA
"""

DEFRA_IPCC_DATA = [
    # --- SCOPE 1: FUELS (YAKITLAR) ---
    # Gaseous Fuels
    {"source": "Doğal Gaz", "fuel_type": "Natural Gas", "factor_value": 2.02266, "unit": "kg CO2e/m3", "scope": 1, "category": "Gaseous Fuels", "ref": "DEFRA 2023"},
    {"source": "Doğal Gaz", "fuel_type": "Natural Gas", "factor_value": 0.18293, "unit": "kg CO2e/kWh", "scope": 1, "category": "Gaseous Fuels", "ref": "DEFRA 2023"},
    {"source": "LNG", "fuel_type": "LNG", "factor_value": 1.15597, "unit": "kg CO2e/kg", "scope": 1, "category": "Gaseous Fuels", "ref": "DEFRA 2023"},
    {"source": "LNG", "fuel_type": "LNG", "factor_value": 0.49327, "unit": "kg CO2e/liter", "scope": 1, "category": "Gaseous Fuels", "ref": "DEFRA 2023"},
    {"source": "LPG", "fuel_type": "LPG", "factor_value": 2.93913, "unit": "kg CO2e/kg", "scope": 1, "category": "Gaseous Fuels", "ref": "DEFRA 2023"},
    {"source": "LPG", "fuel_type": "LPG", "factor_value": 1.55709, "unit": "kg CO2e/liter", "scope": 1, "category": "Gaseous Fuels", "ref": "DEFRA 2023"},
    {"source": "Biogaz", "fuel_type": "Biogas", "factor_value": 0.00021, "unit": "kg CO2e/kWh", "scope": 1, "category": "Gaseous Fuels", "ref": "DEFRA 2023"},

    # Liquid Fuels
    {"source": "Motorin (%100 Mineral)", "fuel_type": "Diesel (100% mineral)", "factor_value": 2.70553, "unit": "kg CO2e/liter", "scope": 1, "category": "Liquid Fuels", "ref": "DEFRA 2023"},
    {"source": "Motorin (Ortalama Biyo katkılı)", "fuel_type": "Diesel (average bio)", "factor_value": 2.51233, "unit": "kg CO2e/liter", "scope": 1, "category": "Liquid Fuels", "ref": "DEFRA 2023"},
    {"source": "Benzin (%100 Mineral)", "fuel_type": "Petrol (100% mineral)", "factor_value": 2.33969, "unit": "kg CO2e/liter", "scope": 1, "category": "Liquid Fuels", "ref": "DEFRA 2023"},
    {"source": "Benzin (Ortalama Biyo katkılı)", "fuel_type": "Petrol (average bio)", "factor_value": 2.11697, "unit": "kg CO2e/liter", "scope": 1, "category": "Liquid Fuels", "ref": "DEFRA 2023"},
    {"source": "Fuel Oil", "fuel_type": "Fuel Oil", "factor_value": 3.17522, "unit": "kg CO2e/kg", "scope": 1, "category": "Liquid Fuels", "ref": "DEFRA 2023"},
    {"source": "Gaz Yağı", "fuel_type": "Burning Oil", "factor_value": 2.54039, "unit": "kg CO2e/liter", "scope": 1, "category": "Liquid Fuels", "ref": "DEFRA 2023"},

    # Solid Fuels
    {"source": "Kömür (Sanayi)", "fuel_type": "Coal (Industrial)", "factor_value": 2441.34, "unit": "kg CO2e/tonne", "scope": 1, "category": "Solid Fuels", "ref": "DEFRA 2023"},
    {"source": "Kömür (Evsel)", "fuel_type": "Coal (Domestic)", "factor_value": 2883.26, "unit": "kg CO2e/tonne", "scope": 1, "category": "Solid Fuels", "ref": "DEFRA 2023"},
    {"source": "Odun Peleti", "fuel_type": "Wood Pellets", "factor_value": 53.06, "unit": "kg CO2e/tonne", "scope": 1, "category": "Solid Fuels", "ref": "DEFRA 2023"},

    # --- SCOPE 2: ELECTRICITY (ELEKTRİK) ---
    {"source": "Elektrik (Türkiye)", "fuel_type": "Electricity (TR)", "factor_value": 0.436, "unit": "kg CO2e/kWh", "scope": 2, "category": "Electricity", "ref": "IEA 2022"},
    {"source": "Elektrik (Avrupa Ort.)", "fuel_type": "Electricity (EU)", "factor_value": 0.254, "unit": "kg CO2e/kWh", "scope": 2, "category": "Electricity", "ref": "EEA 2023"},
    {"source": "Elektrik (ABD)", "fuel_type": "Electricity (US)", "factor_value": 0.385, "unit": "kg CO2e/kWh", "scope": 2, "category": "Electricity", "ref": "EPA 2023"},
    {"source": "Elektrik (Çin)", "fuel_type": "Electricity (CN)", "factor_value": 0.555, "unit": "kg CO2e/kWh", "scope": 2, "category": "Electricity", "ref": "IEA 2022"},

    # --- SCOPE 3: TRANSPORT (ULAŞIM) ---
    # Passenger Vehicles
    {"source": "Binek Araç (Küçük - Dizel)", "fuel_type": "Car (Small Diesel)", "factor_value": 0.13673, "unit": "kg CO2e/km", "scope": 3, "category": "Transport", "ref": "DEFRA 2023"},
    {"source": "Binek Araç (Orta - Dizel)", "fuel_type": "Car (Medium Diesel)", "factor_value": 0.16482, "unit": "kg CO2e/km", "scope": 3, "category": "Transport", "ref": "DEFRA 2023"},
    {"source": "Binek Araç (Büyük - Dizel)", "fuel_type": "Car (Large Diesel)", "factor_value": 0.20739, "unit": "kg CO2e/km", "scope": 3, "category": "Transport", "ref": "DEFRA 2023"},
    {"source": "Binek Araç (Küçük - Benzin)", "fuel_type": "Car (Small Petrol)", "factor_value": 0.14207, "unit": "kg CO2e/km", "scope": 3, "category": "Transport", "ref": "DEFRA 2023"},
    {"source": "Binek Araç (Orta - Benzin)", "fuel_type": "Car (Medium Petrol)", "factor_value": 0.18342, "unit": "kg CO2e/km", "scope": 3, "category": "Transport", "ref": "DEFRA 2023"},
    {"source": "Binek Araç (Elektrikli)", "fuel_type": "Car (EV)", "factor_value": 0.045, "unit": "kg CO2e/km", "scope": 3, "category": "Transport", "ref": "DEFRA 2023 (Grid mix)"},

    # Air Travel
    {"source": "Uçuş (İç Hat)", "fuel_type": "Flight (Domestic)", "factor_value": 0.24628, "unit": "kg CO2e/pkm", "scope": 3, "category": "Transport", "ref": "DEFRA 2023"},
    {"source": "Uçuş (Kısa Mesafe - Ekonomi)", "fuel_type": "Flight (Short haul economy)", "factor_value": 0.15102, "unit": "kg CO2e/pkm", "scope": 3, "category": "Transport", "ref": "DEFRA 2023"},
    {"source": "Uçuş (Uzun Mesafe - Ekonomi)", "fuel_type": "Flight (Long haul economy)", "factor_value": 0.14787, "unit": "kg CO2e/pkm", "scope": 3, "category": "Transport", "ref": "DEFRA 2023"},
    {"source": "Uçuş (Uzun Mesafe - Business)", "fuel_type": "Flight (Long haul business)", "factor_value": 0.42882, "unit": "kg CO2e/pkm", "scope": 3, "category": "Transport", "ref": "DEFRA 2023"},

    # Freight (Nakliye)
    {"source": "Kamyonet (Dizel)", "fuel_type": "Van (Diesel)", "factor_value": 0.23963, "unit": "kg CO2e/km", "scope": 3, "category": "Freight", "ref": "DEFRA 2023"},
    {"source": "Ağır Vasıta (Tır - Ort.)", "fuel_type": "HGV (Articulated)", "factor_value": 0.08298, "unit": "kg CO2e/tkm", "scope": 3, "category": "Freight", "ref": "DEFRA 2023"},
    {"source": "Deniz Taşımacılığı (Konteyner)", "fuel_type": "Sea Freight", "factor_value": 0.01732, "unit": "kg CO2e/tkm", "scope": 3, "category": "Freight", "ref": "DEFRA 2023"},
    {"source": "Hava Kargo", "fuel_type": "Air Freight", "factor_value": 2.15693, "unit": "kg CO2e/tkm", "scope": 3, "category": "Freight", "ref": "DEFRA 2023"},

    # --- SCOPE 3: MATERIAL & WASTE (MALZEME VE ATIK) ---
    # Materials
    {"source": "Su (Şebeke)", "fuel_type": "Water Supply", "factor_value": 0.149, "unit": "kg CO2e/m3", "scope": 3, "category": "Material", "ref": "DEFRA 2023"},
    {"source": "Kağıt", "fuel_type": "Paper", "factor_value": 919.4, "unit": "kg CO2e/tonne", "scope": 3, "category": "Material", "ref": "DEFRA 2023"},
    {"source": "Plastik (Ortalama)", "fuel_type": "Plastic (Average)", "factor_value": 3073.0, "unit": "kg CO2e/tonne", "scope": 3, "category": "Material", "ref": "DEFRA 2023"},
    {"source": "Alüminyum (Kutular)", "fuel_type": "Aluminum Cans", "factor_value": 9109.0, "unit": "kg CO2e/tonne", "scope": 3, "category": "Material", "ref": "DEFRA 2023"},
    {"source": "Çelik (Kutular)", "fuel_type": "Steel Cans", "factor_value": 2862.0, "unit": "kg CO2e/tonne", "scope": 3, "category": "Material", "ref": "DEFRA 2023"},
    {"source": "Cam", "fuel_type": "Glass", "factor_value": 1424.0, "unit": "kg CO2e/tonne", "scope": 3, "category": "Material", "ref": "DEFRA 2023"},
    {"source": "Giyim/Tekstil", "fuel_type": "Clothing", "factor_value": 22310.0, "unit": "kg CO2e/tonne", "scope": 3, "category": "Material", "ref": "DEFRA 2023"},

    # Waste Disposal (Atık Bertarafı)
    {"source": "Atık (Düzenli Depolama)", "fuel_type": "Waste (Landfill)", "factor_value": 467.0, "unit": "kg CO2e/tonne", "scope": 3, "category": "Waste", "ref": "DEFRA 2023"},
    {"source": "Atık (Geri Dönüşüm - Kağıt)", "fuel_type": "Waste (Recycling Paper)", "factor_value": 21.28, "unit": "kg CO2e/tonne", "scope": 3, "category": "Waste", "ref": "DEFRA 2023"},
    {"source": "Atık (Geri Dönüşüm - Plastik)", "fuel_type": "Waste (Recycling Plastic)", "factor_value": 21.28, "unit": "kg CO2e/tonne", "scope": 3, "category": "Waste", "ref": "DEFRA 2023"},
    {"source": "Atık (Kompost)", "fuel_type": "Waste (Composting)", "factor_value": 10.2, "unit": "kg CO2e/tonne", "scope": 3, "category": "Waste", "ref": "DEFRA 2023"},
]
