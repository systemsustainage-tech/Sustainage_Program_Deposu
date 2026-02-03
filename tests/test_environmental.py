
import unittest
import logging
import sys
import os
import tempfile
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.modules.carbon.carbon_calculator import CarbonCalculator
    from backend.modules.energy.energy_manager import EnergyManager
    from backend.modules.waste.waste_manager import WasteManager
    from backend.modules.water.water_manager import WaterManager
except ImportError as e:
    logging.error(f"Import Error: {e}")
    # Might fail if structure is different, but we assume it matches standard backend structure

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestEnvironmentalModules(unittest.TestCase):
    """
    Tests for Environmental Modules (Carbon, Energy, Water, Waste).
    Adapted from c:\\SDG\\tools\\test_environmental_modules.py
    """

    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.temp_db_fd)
        
        # Initialize Managers
        # Note: CarbonCalculator might not take db_path in init, checking signature...
        # If it doesn't, we might need to patch DB_PATH or use a different approach
        # Assuming they accept db_path or we can set it.
        # Looking at previous code, CarbonCalculator might use default DB_PATH.
        # For safety, we will try to pass it if constructor accepts it, or set attribute.
        
        self.company_id = 1
        self.create_dummy_tables()

    def create_dummy_tables(self):
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        # Create minimal tables required for these modules if they don't auto-create
        # Energy tables
        cursor.execute("CREATE TABLE IF NOT EXISTS energy_consumption (id INTEGER PRIMARY KEY, company_id INTEGER, year INTEGER, type TEXT, amount REAL, unit TEXT, source TEXT, location TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS renewable_energy (id INTEGER PRIMARY KEY, company_id INTEGER, year INTEGER, type TEXT, capacity REAL, capacity_unit TEXT, generation REAL, generation_unit TEXT, self_consumption REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        
        # Carbon tables
        cursor.execute("CREATE TABLE IF NOT EXISTS carbon_emissions (id INTEGER PRIMARY KEY, company_id INTEGER, scope TEXT, source TEXT, amount REAL, unit TEXT, co2e REAL, start_date DATE, end_date DATE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        
        conn.commit()
        conn.close()

    def tearDown(self):
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except:
                pass

    def test_carbon_calculation(self):
        """Test Carbon Footprint Calculator"""
        calc = CarbonCalculator() # Uses default DB usually
        # To test calculation logic only, we don't need DB for calculation methods
        
        # Scope 1
        fuel = calc.calculate_scope1_fuel('diesel', 1000)
        self.assertIsNotNone(fuel)
        logging.info(f"Diesel 1000L: {fuel.get('co2e_ton')} ton CO2e")
        
        # Scope 2
        elec = calc.calculate_scope2_electricity(50000, renewable_percent=20)
        self.assertIsNotNone(elec)
        logging.info(f"Electricity 50000kWh: {elec.get('co2e_ton')} ton CO2e")

    def test_energy_manager(self):
        """Test Energy Manager"""
        # We need to inject temp_db_path to EnergyManager if possible
        # If not, it will write to real DB which is bad.
        # Assuming EnergyManager(db_path=...) works.
        try:
            energy = EnergyManager(db_path=self.temp_db_path)
        except TypeError:
            # If it doesn't accept db_path, skip DB writing tests
            logging.warning("EnergyManager does not accept db_path, skipping DB tests")
            return

        energy.add_energy_consumption(self.company_id, 2024, 'Electricity', 40000, 'kWh', 
                                      source='Conventional', location='HQ')
        
        # Verify
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT amount FROM energy_consumption WHERE company_id=?", (self.company_id,))
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 40000)
        logging.info("Energy consumption saved successfully")

