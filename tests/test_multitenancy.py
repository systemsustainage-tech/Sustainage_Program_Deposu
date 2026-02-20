import unittest
import os
import sqlite3
import shutil
from backend.modules.sdg.sdg_manager import SDGManager
from backend.modules.stakeholder.stakeholder_manager import StakeholderManager
from backend.core.database_manager import DatabaseManager

class TestMultitenancy(unittest.TestCase):
    def setUp(self):
        self.test_db = os.path.abspath("tests/test_sdg.sqlite")
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                pass
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.test_db), exist_ok=True)
        
        # Reset DatabaseManager Singleton to ensure fresh start
        DatabaseManager._instance = None
        
        # Initialize Manager (creates tables)
        self.manager = SDGManager(self.test_db)
        
        # Seed global data (goals) manually as they are static
        self.seed_global_data()

    def tearDown(self):
        self.manager.db.close_all()
        # Reset Singleton
        DatabaseManager._instance = None
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                pass

    def seed_global_data(self):
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS sdg_goals (id INTEGER PRIMARY KEY, code TEXT, name_tr TEXT, name_en TEXT, description_tr TEXT, icon TEXT)")
        c.execute("INSERT INTO sdg_goals (code, name_tr) VALUES ('1', 'Yoksulluğa Son')")
        
        # Add companies table for FK constraints
        c.execute("CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY, name TEXT)")
        c.execute("INSERT INTO companies (id, name) VALUES (1, 'Company A')")
        c.execute("INSERT INTO companies (id, name) VALUES (2, 'Company B')")
        
        # Add users table
        c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, company_id INTEGER)")
        c.execute("INSERT INTO users (id, username, company_id) VALUES (1, 'user1', 1)")
        c.execute("INSERT INTO users (id, username, company_id) VALUES (2, 'user2', 2)")
        
        conn.commit()
        conn.close()

    def test_survey_isolation(self):
        from backend.modules.surveys.survey_builder import SurveyBuilder
        
        sb = SurveyBuilder(self.test_db)
        
        # Create templates for Company 1
        sb.set_company_context(1)
        sb.create_sample_data() # Creates templates and questions for company 1
        
        # Create templates for Company 2
        sb.set_company_context(2)
        sb.create_sample_data() # Creates templates and questions for company 2
        
        # Assign survey to User 1 (Company 1)
        sb.set_company_context(1)
        # Get template for company 1
        tpl1 = sb.select_one('survey_templates', company_id=1, order_by='id ASC')
        self.assertIsNotNone(tpl1)
        
        # Assign
        sb.insert('user_surveys', {
            'user_id': 1,
            'template_id': tpl1['id'],
            'assigned_by': 1,
            'status': 'assigned'
        }, company_id=1)
        
        # Assign survey to User 2 (Company 2)
        sb.set_company_context(2)
        tpl2 = sb.select_one('survey_templates', company_id=2, order_by='id DESC')
        self.assertIsNotNone(tpl2)
        
        sb.insert('user_surveys', {
            'user_id': 2,
            'template_id': tpl2['id'],
            'assigned_by': 2,
            'status': 'assigned'
        }, company_id=2)
        
        # Verify isolation: User 1 should see only their survey
        sb.set_company_context(1)
        surveys1 = sb.get_user_surveys(user_id=1)
        self.assertEqual(len(surveys1), 1)
        self.assertEqual(surveys1[0]['title'], tpl1['name'])
        
        # Verify isolation: User 2 should see only their survey
        sb.set_company_context(2)
        surveys2 = sb.get_user_surveys(user_id=2)
        self.assertEqual(len(surveys2), 1)
        self.assertEqual(surveys2[0]['title'], tpl2['name'])
        
        # Verify cross-access protection (User 1 trying to see User 2's survey via company 1 context)
        # Assuming user_survey_id of user 2 is known (likely 2)
        sb.set_company_context(1)
        detail = sb.get_user_survey_detail(user_survey_id=2) # 2 belongs to company 2
        self.assertIsNone(detail)
        
        # Verify correct access
        sb.set_company_context(2)
        detail = sb.get_user_survey_detail(user_survey_id=2)
        self.assertIsNotNone(detail)
        self.assertEqual(detail['user_id'], 2)

    def test_tenant_isolation(self):
        # Company 1 saves a response
        self.manager.save_response(company_id=1, indicator_id=101, period="2023", value="100", unit="kg")
        
        # Company 2 saves a response for same indicator/period
        self.manager.save_response(company_id=2, indicator_id=101, period="2023", value="200", unit="kg")
        
        # Check Company 1
        resp1 = self.manager.get_response(company_id=1, indicator_id=101, period="2023")
        self.assertEqual(resp1['value'], "100")
        
        # Check Company 2
        resp2 = self.manager.get_response(company_id=2, indicator_id=101, period="2023")
        self.assertEqual(resp2['value'], "200")
        
        # Check Statistics
        stats1 = self.manager.get_statistics(company_id=1)
        self.assertEqual(stats1['completed_actions'], 1)
        
        stats2 = self.manager.get_statistics(company_id=2)
        self.assertEqual(stats2['completed_actions'], 1)

    def test_stakeholder_isolation(self):
        sm = StakeholderManager(self.test_db)
        
        # Company 1 adds stakeholder
        sm.add_stakeholder(company_id=1, stakeholder_name="Partner A", stakeholder_type="Customer")
        
        # Company 2 adds stakeholder
        sm.add_stakeholder(company_id=2, stakeholder_name="Partner B", stakeholder_type="Supplier")
        
        # Check counts
        stats1 = sm.get_dashboard_stats(company_id=1)
        self.assertEqual(stats1['total_stakeholders'], 1)
        
        stats2 = sm.get_dashboard_stats(company_id=2)
        self.assertEqual(stats2['total_stakeholders'], 1)
        
        # Verify isolation via action plan update
        sm.add_action_plan(company_id=1, title="Plan A")
        plans1 = sm.get_action_plans(company_id=1)
        self.assertTrue(len(plans1) > 0)
        plan_id = plans1[0]['id']
        
        # Try to update with company_id=2 (should fail/return False as it affects 0 rows)
        success = sm.update_action_plan_status(plan_id, "closed", company_id=2)
        self.assertFalse(success)
        
        # Correct update with company_id=1
        success = sm.update_action_plan_status(plan_id, "closed", company_id=1)
        self.assertTrue(success)

    def test_selected_goals_isolation(self):
        # Company 1 selects goal 1
        self.manager.save_selected_goals(company_id=1, goal_ids=[1])
        
        # Company 2 selects nothing
        self.manager.save_selected_goals(company_id=2, goal_ids=[])
        
        sel1 = self.manager.get_selected_goals(company_id=1)
        self.assertEqual(sel1, [1])
        
        sel2 = self.manager.get_selected_goals(company_id=2)
        self.assertEqual(sel2, [])

    def test_global_data_access(self):
        goals = self.manager.get_all_goals()
        self.assertTrue(len(goals) > 0)
        self.assertEqual(goals[0]['code'], '1')

    def test_esg_isolation(self):
        from backend.modules.esg.esg_manager import ESGManager
        
        # Monkey patch _load_config to control db_path
        original_load_config = ESGManager._load_config
        def mock_load_config(obj):
            return {
                'weights': {'E': 0.4, 'S': 0.3, 'G': 0.3},
                'sources': {'db_path': 'test_sdg.sqlite'}, 
                'scoring': {
                    'min_completeness_to_count': 0.5,
                    'evidence_bonus': 0.05,
                    'materiality_bonus': 0.1,
                    'normalize_method': 'ratio_answered_to_total'
                },
                'mappings': {
                    'E': {'gri_categories': ['Environmental'], 'tsrs_sections': ['TSRS-E1','TSRS-E2','TSRS-E3','TSRS-E4','TSRS-E5']},
                    'S': {'gri_categories': ['Social'], 'tsrs_sections': ['TSRS-S1','TSRS-S2','TSRS-S3','TSRS-S4']},
                    'G': {'gri_standards': ['GRI 2'], 'tsrs_sections': ['TSRS-G1']}
                }
            }
        ESGManager._load_config = mock_load_config
        
        try:
            # base_dir will be the directory of test_db
            base_dir = os.path.dirname(self.test_db)
            em = ESGManager(base_dir) 
            
            # Company 1 saves score
            em.save_score(company_id=1, year=2023, quarter=1, e_score=80, s_score=70, g_score=90, total=80)
            
            # Company 2 saves score
            em.save_score(company_id=2, year=2023, quarter=1, e_score=50, s_score=50, g_score=50, total=50)
            
            # Check history
            hist1 = em.get_history(company_id=1)
            self.assertEqual(len(hist1), 1)
            self.assertEqual(hist1[0]['overall'], 80.0)
            
            hist2 = em.get_history(company_id=2)
            self.assertEqual(len(hist2), 1)
            self.assertEqual(hist2[0]['overall'], 50.0)
            
            # Check data availability isolation
            # Create carbon_emissions table manually as it is an external source
            em.execute_update("CREATE TABLE IF NOT EXISTS carbon_emissions (id INTEGER PRIMARY KEY, company_id INTEGER)")
            em.execute_update("INSERT INTO carbon_emissions (company_id) VALUES (1)")
            
            da1 = em._check_data_availability(company_id=1)
            self.assertTrue(da1['carbon'])
            
            da2 = em._check_data_availability(company_id=2)
            self.assertFalse(da2['carbon'])
            
        finally:
            ESGManager._load_config = original_load_config

    def test_detailed_energy_isolation(self):
        from backend.modules.environmental.detailed_energy_manager import DetailedEnergyManager
        
        em = DetailedEnergyManager(self.test_db)
        
        # Company 1
        em.set_company_context(1)
        em.record_energy_consumption(
            consumption_amount=100, 
            unit='kWh', 
            energy_type='electricity',
            cost=500
        )
        
        # Company 2
        em.set_company_context(2)
        em.record_energy_consumption(
            consumption_amount=200, 
            unit='kWh', 
            energy_type='electricity',
            cost=1000
        )
        
        # Verify Company 1
        em.set_company_context(1)
        metrics1 = em.calculate_energy_metrics()
        self.assertEqual(metrics1['total_consumption'], 100)
        self.assertEqual(metrics1['total_cost'], 500)
        
        # Verify Company 2
        em.set_company_context(2)
        metrics2 = em.calculate_energy_metrics()
        self.assertEqual(metrics2['total_consumption'], 200)
        self.assertEqual(metrics2['total_cost'], 1000)


    # Removed duplicate test_cbam_isolation

    def test_hosting_survey_isolation(self):
        from backend.modules.surveys.hosting_survey_manager import HostingSurveyManager
        
        hm = HostingSurveyManager(self.test_db)
        
        # Company 1
        hm.set_company_context(1)
        hm._save_survey_locally({
            'survey_id': 101,
            'survey_name': 'Survey 1',
            'company_name': 'Company A',
            'survey_url': 'http://url1',
            'token': 'token1'
        })
        
        # Company 2
        hm.set_company_context(2)
        hm._save_survey_locally({
            'survey_id': 102,
            'survey_name': 'Survey 2',
            'company_name': 'Company B',
            'survey_url': 'http://url2',
            'token': 'token2'
        })
        
        # Verify Company 1
        hm.set_company_context(1)
        surveys1 = hm.list_local_surveys()
        self.assertEqual(len(surveys1), 1)
        self.assertEqual(surveys1[0]['hosting_survey_id'], 101)
        
        # Verify Company 2
        hm.set_company_context(2)
        surveys2 = hm.list_local_surveys()
        self.assertEqual(len(surveys2), 1)
        self.assertEqual(surveys2[0]['hosting_survey_id'], 102)

    def test_carbon_isolation(self):
        from backend.modules.environmental.carbon_manager import CarbonManager
        
        cm = CarbonManager(self.test_db)
        
        # Company 1
        cm.set_company_context(1)
        # Add Scope 1 emission (Natural Gas is in defaults)
        success1 = cm.add_scope1_emission(
            company_id=1,
            year=2023,
            emission_source="Natural Gas Source",
            fuel_type="Natural Gas",
            fuel_consumption=1000,
            fuel_unit="m3"
        )
        self.assertTrue(success1)
        
        # Add Scope 2 emission (Electricity is in defaults)
        success2 = cm.add_scope2_emission(
            company_id=1,
            year=2023,
            energy_source="Grid",
            energy_consumption=5000,
            energy_unit="kWh"
        )
        self.assertTrue(success2)
        
        # Company 2
        cm.set_company_context(2)
        # Add Scope 1 emission (Diesel is in defaults)
        success3 = cm.add_scope1_emission(
            company_id=2,
            year=2023,
            emission_source="Diesel Generator",
            fuel_type="Diesel",
            fuel_consumption=2000,
            fuel_unit="liters"
        )
        self.assertTrue(success3)
        
        # Verify Company 1
        cm.set_company_context(1)
        total1 = cm.get_total_carbon_footprint(company_id=1, year=2023)
        self.assertGreater(total1, 0)
        
        records1 = cm.get_recent_records(company_id=1, limit=100)
        # Should have 2 records (Scope 1 and Scope 2)
        self.assertEqual(len(records1), 2)
        sources1 = {r['category'] for r in records1} # 'category' alias in get_recent_records maps to emission_source/energy_source
        self.assertIn("Natural Gas Source", sources1)
        self.assertIn("Grid", sources1)
        self.assertNotIn("Diesel Generator", sources1)
        
        # Verify Company 2
        cm.set_company_context(2)
        total2 = cm.get_total_carbon_footprint(company_id=2, year=2023)
        self.assertGreater(total2, 0)
        self.assertNotEqual(total1, total2)
        
        records2 = cm.get_recent_records(company_id=2, limit=100)
        # Should have 1 record
        self.assertEqual(len(records2), 1)
        self.assertEqual(records2[0]['category'], "Diesel Generator")

    def test_waste_isolation(self):
        from backend.modules.environmental.waste_manager import WasteManager
        
        wm = WasteManager(self.test_db)
        
        # Company 1
        wm.set_company_context(1)
        wm.add_waste_generation(
            company_id=1,
            year=2023,
            waste_type="Paper",
            waste_category="Recyclable",
            waste_amount=100,
            unit="kg",
            disposal_method="Recycling"
        )
        
        # Company 2
        wm.set_company_context(2)
        wm.add_waste_generation(
            company_id=2,
            year=2023,
            waste_type="Chemical",
            waste_category="Hazardous",
            waste_amount=50,
            unit="kg",
            disposal_method="Special Treatment"
        )
        
        # Verify Company 1
        wm.set_company_context(1)
        stats1 = wm.get_dashboard_stats(company_id=1)
        self.assertEqual(stats1['total_waste'], 100)
        
        records1 = wm.get_waste_records(company_id=1)
        self.assertEqual(len(records1), 1)
        self.assertEqual(records1[0]['waste_type'], "Paper")
        
        # Verify Company 2
        wm.set_company_context(2)
        stats2 = wm.get_dashboard_stats(company_id=2)
        self.assertEqual(stats2['total_waste'], 50)
        
        records2 = wm.get_waste_records(company_id=2)
        self.assertEqual(len(records2), 1)
        self.assertEqual(records2[0]['waste_type'], "Chemical")

    def test_water_isolation(self):
        from backend.modules.environmental.water_manager import WaterManager
        
        wm = WaterManager(self.test_db)
        
        # Company 1
        wm.set_company_context(1)
        wm.add_water_consumption(
            company_id=1,
            year=2023,
            consumption_type="Mains",
            consumption_amount=1000,
            unit="m3",
            source="Municipal"
        )
        
        # Company 2
        wm.set_company_context(2)
        wm.add_water_consumption(
            company_id=2,
            year=2023,
            consumption_type="Groundwater",
            consumption_amount=500,
            unit="m3",
            source="Well"
        )
        
        # Verify Company 1
        wm.set_company_context(1)
        stats1 = wm.get_dashboard_stats(company_id=1)
        self.assertEqual(stats1['total_consumption'], 1000)
        
        records1 = wm.get_water_records(company_id=1)
        self.assertEqual(len(records1), 1)
        self.assertEqual(records1[0]['category'], "Mains")
        
        # Verify Company 2
        wm.set_company_context(2)
        stats2 = wm.get_dashboard_stats(company_id=2)
        self.assertEqual(stats2['total_consumption'], 500)
        
        records2 = wm.get_water_records(company_id=2)
        self.assertEqual(len(records2), 1)
        self.assertEqual(records2[0]['category'], "Groundwater")

    def test_energy_isolation(self):
        from backend.modules.environmental.energy_manager import EnergyManager
        
        em = EnergyManager(self.test_db)
        
        # Company 1
        em.set_company_context(1)
        em.add_energy_consumption(
            company_id=1,
            year=2023,
            month=1,
            energy_type="Grid",
            consumption_amount=1000,
            unit="kWh",
            cost=500,
            source="Grid",
            location="Building A",
            invoice_date="2023-01-01",
            due_date="2023-01-15",
            supplier="Utility Co"
        )
        
        # Company 2
        em.set_company_context(2)
        em.add_energy_consumption(
            company_id=2,
            year=2023,
            month=1,
            energy_type="Solar",
            consumption_amount=2000,
            unit="kWh",
            cost=1000,
            source="Solar",
            location="Building B",
            invoice_date="2023-01-01",
            due_date="2023-01-15",
            supplier="Solar Co"
        )
        
        # Verify Company 1
        em.set_company_context(1)
        stats1 = em.get_dashboard_stats(company_id=1)
        self.assertEqual(stats1['total_consumption'], 1000)
        self.assertEqual(stats1['total_cost'], 500)
        
        # Verify Company 2
        em.set_company_context(2)
        stats2 = em.get_dashboard_stats(company_id=2)
        self.assertEqual(stats2['total_consumption'], 2000)
        self.assertEqual(stats2['total_cost'], 1000)

    def test_biodiversity_isolation(self):
        from backend.modules.environmental.biodiversity_manager import BiodiversityManager
        
        bm = BiodiversityManager(self.test_db)
        
        # Company 1
        bm.set_company_context(1)
        bm.add_habitat_area(
            company_id=1,
            habitat_name="Protected Forest",
            habitat_type="Forest",
            area_size=100,
            area_unit="ha",
            location="Region A"
        )
        
        # Company 2
        bm.set_company_context(2)
        bm.add_habitat_area(
            company_id=2,
            habitat_name="Coastal Wetland",
            habitat_type="Wetland",
            area_size=50,
            area_unit="ha",
            location="Region B"
        )
        
        # Verify Company 1
        bm.set_company_context(1)
        stats1 = bm.get_dashboard_stats(company_id=1)
        self.assertEqual(stats1['habitat_count'], 1)
        self.assertEqual(stats1['total_area'], 100)
        
        records1 = bm.get_recent_records(company_id=1)
        self.assertEqual(len(records1), 1)
        # Check against mapped fields in get_recent_records
        # description maps to habitat_name
        self.assertEqual(records1[0]['description'], "Protected Forest")
        
        # Verify Company 2
        bm.set_company_context(2)
        stats2 = bm.get_dashboard_stats(company_id=2)
        self.assertEqual(stats2['habitat_count'], 1)
        self.assertEqual(stats2['total_area'], 50)
        
        records2 = bm.get_recent_records(company_id=2)
        self.assertEqual(len(records2), 1)
        self.assertEqual(records2[0]['description'], "Coastal Wetland")

    def test_cbam_isolation(self):
        """Test CBAM data isolation between tenants"""
        from backend.modules.cbam.cbam_manager import CBAMManager
        
        cm = CBAMManager(self.test_db)
        
        # Company 1: Add product and import
        cm.set_company_context(1)
        # Add product first
        cm.execute_update(
            "INSERT INTO cbam_products (company_id, product_code, product_name, cn_code, sector) VALUES (?, ?, ?, ?, ?)",
            (1, "P1", "Steel Rods", "7214", "Iron and Steel")
        )
        # Get product ID
        prod1 = cm.execute_query("SELECT id FROM cbam_products WHERE company_id = 1")[0]['id']
        
        # Add import
        cm.add_import(
            company_id=1,
            product_id=prod1,
            origin_country="TR",
            quantity=1000,
            embedded_emissions=1850.0, # 1.85 * 1000
            carbon_price_paid=0.0
        )
        
        # Company 2: Add product and import
        cm.set_company_context(2)
        cm.execute_update(
            "INSERT INTO cbam_products (company_id, product_code, product_name, cn_code, sector) VALUES (?, ?, ?, ?, ?)",
            (2, "P2", "Cement Clinker", "2523", "Cement")
        )
        prod2 = cm.execute_query("SELECT id FROM cbam_products WHERE company_id = 2")[0]['id']
        
        cm.add_import(
            company_id=2,
            product_id=prod2,
            origin_country="DE",
            quantity=500,
            embedded_emissions=475.0, # 0.95 * 500
            carbon_price_paid=0.0
        )
        
        # Verify Company 1
        cm.set_company_context(1)
        stats1 = cm.calculate_cbam_metrics(company_id=1)
        # Total imports: 1000
        self.assertEqual(stats1['total_imports'], 1000)
        # Check imports list
        imports1 = stats1['imports']
        self.assertEqual(len(imports1), 1)
        self.assertEqual(imports1[0]['product_name'], "Steel Rods")
        
        # Verify Company 2
        cm.set_company_context(2)
        stats2 = cm.calculate_cbam_metrics(company_id=2)
        # Total imports: 500
        self.assertEqual(stats2['total_imports'], 500)
        # Check imports list
        imports2 = stats2['imports']
        self.assertEqual(len(imports2), 1)
        self.assertEqual(imports2[0]['product_name'], "Cement Clinker")

    # Removed duplicate test_carbon_isolation

    def test_api_manager_isolation(self):
        """Test API Manager isolation"""
        from backend.modules.integration.api_manager import APIManager
        
        am = APIManager(self.test_db)
        
        # Company 1
        am.set_company_context(1)
        am.add_api_endpoint(
            company_id=1,
            endpoint_name="Endpoint A",
            endpoint_url="/api/v1/a",
            http_method="GET",
            description="Test Endpoint A",
            authentication_type="API Key",
            rate_limit=100
        )
        
        # Company 2
        am.set_company_context(2)
        am.add_api_endpoint(
            company_id=2,
            endpoint_name="Endpoint B",
            endpoint_url="/api/v1/b",
            http_method="POST",
            description="Test Endpoint B",
            authentication_type="Bearer",
            rate_limit=200
        )
        
        # Verify Company 1
        am.set_company_context(1)
        summary1 = am.get_api_summary(company_id=1)
        self.assertEqual(len(summary1['endpoints']), 1)
        self.assertEqual(summary1['endpoints'][0]['endpoint_name'], "Endpoint A")
        
        # Verify Company 2
        am.set_company_context(2)
        summary2 = am.get_api_summary(company_id=2)
        self.assertEqual(len(summary2['endpoints']), 1)
        self.assertEqual(summary2['endpoints'][0]['endpoint_name'], "Endpoint B")

    def test_regulation_isolation(self):
        """Test Regulation Manager isolation"""
        from backend.modules.regulation.regulation_manager import RegulationManager
        
        rm = RegulationManager(self.test_db)
        
        # Company 1
        rm.set_company_context(1)
        # Add a regulation first (shared data usually, but compliance is per company)
        # Note: Regulations themselves might be global, but compliance is per company.
        # Let's check how add_regulation works. It adds to 'regulations' table.
        # If regulations are global, we should check compliance status isolation.
        
        # Add a global regulation
        reg_id = rm.add_regulation(
            code="REG001",
            title="Global Regulation",
            scope="International",
            authority="UN"
        )
        
        # Company 1 updates compliance
        rm.update_compliance_status(
            company_id=1,
            regulation_id=reg_id,
            status="compliant",
            notes="Fully compliant"
        )
        
        # Company 2 updates compliance
        rm.set_company_context(2)
        rm.update_compliance_status(
            company_id=2,
            regulation_id=reg_id,
            status="non_compliant",
            notes="Working on it"
        )
        
        # Verify Company 1
        rm.set_company_context(1)
        compliance1 = rm.get_company_compliance(company_id=1)
        # Should find the regulation and its status for company 1
        found1 = False
        for c in compliance1:
            if c['id'] == reg_id:
                self.assertEqual(c['compliance_status'], "compliant")
                self.assertEqual(c['notes'], "Fully compliant")
                found1 = True
        self.assertTrue(found1)
        
        # Verify Company 2
        rm.set_company_context(2)
        compliance2 = rm.get_company_compliance(company_id=2)
        found2 = False
        for c in compliance2:
            if c['id'] == reg_id:
                self.assertEqual(c['compliance_status'], "non_compliant")
                self.assertEqual(c['notes'], "Working on it")
                found2 = True
        self.assertTrue(found2)

    def test_gri_isolation(self):
        """Test GRI Manager isolation"""
        from backend.modules.gri.gri_manager import GRIManager
        
        gm = GRIManager(self.test_db)
        
        # Company 1
        gm.set_company_context(1)
        # Assuming indicator ID 1 exists (GRI 2-1 created in populate_gri_standards)
        gm.save_gri_response(
            company_id=1,
            indicator_id=1, 
            period="2023",
            response_value="Company 1 Response",
            numerical_value=100.0,
            unit="tons"
        )
        
        # Company 2
        gm.set_company_context(2)
        gm.save_gri_response(
            company_id=2,
            indicator_id=1,
            period="2023",
            response_value="Company 2 Response",
            numerical_value=200.0,
            unit="kg"
        )
        
        # Verify Company 1
        gm.set_company_context(1)
        responses1 = gm.get_gri_responses(company_id=1, period="2023")
        self.assertEqual(len(responses1), 1)
        self.assertEqual(responses1[0]['response_value'], "Company 1 Response")
        self.assertEqual(responses1[0]['numerical_value'], 100.0)
        
        # Verify Company 2
        gm.set_company_context(2)
        responses2 = gm.get_gri_responses(company_id=2, period="2023")
        self.assertEqual(len(responses2), 1)
        self.assertEqual(responses2[0]['response_value'], "Company 2 Response")
        self.assertEqual(responses2[0]['numerical_value'], 200.0)

if __name__ == '__main__':
    unittest.main()
