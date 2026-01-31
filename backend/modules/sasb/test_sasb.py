#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SASB Modülü Test Dosyası
- SASB Manager testleri
- SASB Calculator testleri
- SASB GUI testleri
- SASB Report Generator testleri
"""

import logging
import os
import sqlite3
import sys
import tempfile
import unittest

# Ana modül yollarını ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from modules.sasb.sasb_calculator import SASBCalculator
from modules.sasb.sasb_manager import SASBManager
from modules.sasb.sasb_report_generator import SASBReportGenerator


class TestSASBManager(unittest.TestCase):
    """SASB Manager test sınıfı"""

    def setUp(self):
        """Test öncesi hazırlık"""
        # Geçici veritabanı oluştur
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        self.temp_db.close()

        # SASB Manager'ı başlat
        self.sasb_manager = SASBManager(self.temp_db.name)

        # Test verilerini yükle
        self.sasb_manager.load_sector_data()

    def tearDown(self):
        """Test sonrası temizlik"""
        try:
            os.unlink(self.temp_db.name)
        except PermissionError:
            pass

    def test_database_initialization(self):
        """Veritabanı başlatma testi"""
        # Tabloların oluşturulduğunu kontrol et
        conn = sqlite3.connect(self.temp_db.name)
        cur = conn.cursor()

        # Tabloları listele
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]

        expected_tables = [
            'sasb_sectors', 'sasb_disclosure_topics',
            'sasb_metrics', 'company_sasb_data', 'sasb_metric_responses', 'sasb_gri_mapping',
            'sasb_financial_materiality'
        ]

        for table in expected_tables:
            self.assertIn(table, tables)

        conn.close()

    def test_load_sasb_data(self):
        """SASB veri yükleme testi"""
        # Verilerin yüklendiğini kontrol et
        sectors = self.sasb_manager.get_all_sectors()
        self.assertGreater(len(sectors), 0)

        # Disclosure topics kontrolü (ilk sektör için)
        topics = self.sasb_manager.get_sector_topics(sectors[0]['id'])
        self.assertGreater(len(topics), 0)

    def test_sector_management(self):
        """Sektör yönetimi testi"""
        sectors = self.sasb_manager.get_all_sectors()
        first_sector = sectors[0]
        
        # Şirket için sektör seç
        success = self.sasb_manager.select_company_sector(1, 2024, first_sector['id'])
        self.assertTrue(success)
        
        # Seçilen sektörü getir
        selected = self.sasb_manager.get_company_sector(1, 2024)
        self.assertIsNotNone(selected)
        self.assertEqual(selected['id'], first_sector['id'])

    def test_disclosure_data_management(self):
        """Disclosure veri yönetimi testi"""
        sectors = self.sasb_manager.get_all_sectors()
        self.sasb_manager.select_company_sector(1, 2024, sectors[0]['id'])
        
        topics = self.sasb_manager.get_sector_topics(sectors[0]['id'])
        metrics = self.sasb_manager.get_topic_metrics(topics[0]['id'])
        
        # Metrik yanıtı kaydet
        success = self.sasb_manager.save_metric_response(
            company_id=1,
            metric_id=metrics[0]['id'],
            year=2024,
            response_value="Test Value",
            numerical_value=100.0,
            unit="kg",
            notes="Test Note"
        )
        self.assertTrue(success)
        
        # Yanıtları getir
        responses = self.sasb_manager.get_metric_responses(1, 2024)
        self.assertIn(metrics[0]['id'], responses)
        self.assertEqual(responses[metrics[0]['id']]['response_value'], "Test Value")

class TestSASBCalculator(unittest.TestCase):
    """SASB Calculator test sınıfı"""

    def setUp(self):
        """Test öncesi hazırlık"""
        # Geçici veritabanı oluştur
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        self.temp_db.close()

        # SASB Manager'ı başlat
        self.sasb_manager = SASBManager(self.temp_db.name)
        self.sasb_manager.load_sector_data()

        # SASB Calculator'ı başlat
        self.calculator = SASBCalculator(self.temp_db.name)

        # Test verilerini hazırla
        self._prepare_test_data()

    def tearDown(self):
        """Test sonrası temizlik"""
        try:
            os.unlink(self.temp_db.name)
        except PermissionError:
            pass

    def _prepare_test_data(self):
        """Test verilerini hazırla"""
        # Şirket oluştur
        conn = sqlite3.connect(self.temp_db.name)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        cur.execute("INSERT OR REPLACE INTO companies (id, name) VALUES (?, ?)", (1, "Test Company"))
        conn.commit()
        conn.close()

        # Sektör seç
        sectors = self.sasb_manager.get_all_sectors()
        self.sasb_manager.select_company_sector(1, 2024, sectors[0]['id'])

        # Topics'leri al
        topics = self.sasb_manager.get_sector_topics(sectors[0]['id'])

        # Metrikleri al ve veri kaydet
        for topic in topics[:3]:  # İlk 3 topic
            metrics = self.sasb_manager.get_topic_metrics(topic['id'])
            for metric in metrics[:2]:  # Her topic'ten ilk 2 metrik
                self.sasb_manager.save_metric_response(
                    company_id=1,
                    metric_id=metric['id'],
                    year=2024,
                    response_value="1000",
                    notes="Test data"
                )

    def test_materiality_score_calculation(self):
        """Materiality skoru hesaplama testi"""
        sectors = self.sasb_manager.get_all_sectors()
        score = self.calculator.calculate_materiality_score(1, sectors[0]['id'], 2024)

        self.assertIsNotNone(score)
        self.assertIn('overall_score', score)
        self.assertIn('disclosure_rate', score)
        self.assertIn('materiality_rate', score)
        self.assertIn('dimension_scores', score)
        self.assertIn('grade', score)

    def test_trend_analysis(self):
        """Trend analizi testi"""
        sectors = self.sasb_manager.get_all_sectors()

        # 2023 verisi ekle
        topics = self.sasb_manager.get_sector_topics(sectors[0]['id'])
        for topic in topics[:2]:
            metrics = self.sasb_manager.get_topic_metrics(topic['id'])
            for metric in metrics[:1]:
                self.sasb_manager.save_metric_response(
                    company_id=1,
                    metric_id=metric['id'],
                    year=2023,
                    response_value="800",
                    notes="Test data"
                )

        # Trend analizi yap
        trend = self.calculator.calculate_trend_analysis(1, sectors[0]['id'], [2023, 2024])

        self.assertIsNotNone(trend)
        self.assertIn('years', trend)
        self.assertIn('scores', trend)
        self.assertIn('trend_direction', trend)

    def test_sector_comparison(self):
        """Sektör karşılaştırması testi"""
        sectors = self.sasb_manager.get_all_sectors()

        # İkinci şirket için veri ekle
        conn = sqlite3.connect(self.temp_db.name)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO companies (id, name) VALUES (?, ?)", (2, "Competitor"))
        conn.commit()
        conn.close()

        self.sasb_manager.select_company_sector(2, 2024, sectors[0]['id'])

        comparison = self.calculator.calculate_sector_comparison(1, sectors[0]['id'], 2024)

        self.assertIsNotNone(comparison)
        self.assertIn('company_score', comparison)
        self.assertIn('sector_average', comparison)

    def test_risk_assessment(self):
        """Risk değerlendirmesi testi"""
        sectors = self.sasb_manager.get_all_sectors()
        risk = self.calculator.calculate_risk_assessment(1, sectors[0]['id'], 2024)

        self.assertIsNotNone(risk)
        self.assertIn('overall_risk_score', risk)
        self.assertIn('risk_level', risk)
        self.assertIn('category_scores', risk)

class TestSASBReportGenerator(unittest.TestCase):
    """SASB Report Generator test sınıfı"""

    def setUp(self):
        """Test öncesi hazırlık"""
        # Geçici veritabanı oluştur
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        self.temp_db.close()

        # SASB Manager'ı başlat
        self.sasb_manager = SASBManager(self.temp_db.name)
        self.sasb_manager.load_sector_data()
        
        # Generator'ı başlat
        self.report_generator = SASBReportGenerator(self.temp_db.name)

        # Test verilerini hazırla
        self._prepare_test_data()

    def tearDown(self):
        """Test sonrası temizlik"""
        try:
            os.unlink(self.temp_db.name)
        except PermissionError:
            pass

    def _prepare_test_data(self):
        """Test verilerini hazırla"""
        # Şirket bilgisi ekle
        conn = sqlite3.connect(self.temp_db.name)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)

        cur.execute("INSERT OR REPLACE INTO companies (id, name) VALUES (?, ?)",
                   (1, "Test Company"))

        conn.commit()
        conn.close()

        # Sektör seç
        sectors = self.sasb_manager.get_all_sectors()
        self.sasb_manager.select_company_sector(1, 2024, sectors[0]['id'])

        # Veri kaydet
        topics = self.sasb_manager.get_sector_topics(sectors[0]['id'])
        for topic in topics[:2]:
            metrics = self.sasb_manager.get_topic_metrics(topic['id'])
            for metric in metrics[:1]:
                self.sasb_manager.save_metric_response(
                    company_id=1,
                    metric_id=metric['id'],
                    year=2024,
                    response_value="1000",
                    notes="Test data"
                )

    def test_pdf_report_generation(self):
        """PDF raporu oluşturma testi"""
        # Geçici dosya oluştur
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.close()

        try:
            # PDF raporu oluştur
            success = self.report_generator.generate_pdf_report(1, temp_pdf.name, 2024)
            self.assertTrue(success)

            # Dosyanın oluşturulduğunu kontrol et
            self.assertTrue(os.path.exists(temp_pdf.name))
            self.assertGreater(os.path.getsize(temp_pdf.name), 0)

        finally:
            # Geçici dosyayı sil
            if os.path.exists(temp_pdf.name):
                os.unlink(temp_pdf.name)

    def test_docx_report_generation(self):
        """DOCX raporu oluşturma testi"""
        # Geçici dosya oluştur
        temp_docx = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        temp_docx.close()

        try:
            # DOCX raporu oluştur
            success = self.report_generator.generate_docx_report(1, temp_docx.name, 2024)
            self.assertTrue(success)

            # Dosyanın oluşturulduğunu kontrol et
            self.assertTrue(os.path.exists(temp_docx.name))
            self.assertGreater(os.path.getsize(temp_docx.name), 0)

        finally:
            # Geçici dosyayı sil
            if os.path.exists(temp_docx.name):
                os.unlink(temp_docx.name)

    def test_excel_report_generation(self):
        """Excel raporu oluşturma testi"""
        # Geçici dosya oluştur
        temp_excel = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_excel.close()

        try:
            # Excel raporu oluştur
            success = self.report_generator.generate_excel_report(1, temp_excel.name, 2024)
            self.assertTrue(success)

            # Dosyanın oluşturulduğunu kontrol et
            self.assertTrue(os.path.exists(temp_excel.name))
            self.assertGreater(os.path.getsize(temp_excel.name), 0)

        finally:
            # Geçici dosyayı sil
            if os.path.exists(temp_excel.name):
                os.unlink(temp_excel.name)

def run_tests():
    """Testleri çalıştır"""
    # Test suite oluştur
    test_suite = unittest.TestSuite()

    # Test sınıflarını ekle
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSASBManager))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSASBCalculator))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSASBReportGenerator))

    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)

    # Testleri çalıştır
    result = runner.run(test_suite)

    # Sonuçları yazdır
    logging.info(f"\nToplam Test: {result.testsRun}")
    logging.error(f"Başarılı: {result.testsRun - len(result.failures) - len(result.errors)}")
    logging.error(f"Başarısız: {len(result.failures)}")
    logging.error(f"Hata: {len(result.errors)}")

    if result.failures:
        logging.info("\nBaşarısız Testler:")
        for test, traceback in result.failures:
            logging.info(f"- {test}: {traceback}")

    if result.errors:
        logging.error("\nHatalı Testler:")
        for test, traceback in result.errors:
            logging.info(f"- {test}: {traceback}")

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
