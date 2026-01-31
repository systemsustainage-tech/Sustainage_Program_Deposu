
import os
import sqlite3
import unittest
import sys
import time
from datetime import datetime

# Add project root and backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from backend.modules.super_admin.components.ip_manager import IPManager
from backend.modules.super_admin.components.rate_limiter import RateLimiter
from backend.modules.super_admin.components.monitoring_dashboard import MonitoringDashboard

TEST_DB = "test_super_admin.sqlite"

class TestSuperAdminModule(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Initialize Test DB
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
            
        cls.conn = sqlite3.connect(TEST_DB)
        cls.cursor = cls.conn.cursor()
        
        # Create necessary tables
        cls.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL UNIQUE,
                description TEXT,
                added_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        cls.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL UNIQUE,
                reason TEXT,
                blocked_by TEXT,
                block_type TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        cls.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                resource_type TEXT,
                identifier TEXT,
                request_count INTEGER DEFAULT 0,
                window_start TIMESTAMP,
                last_request TIMESTAMP,
                is_blocked INTEGER DEFAULT 0,
                PRIMARY KEY (resource_type, identifier)
            )
        """)
        
        # Mock tables for MonitoringDashboard
        cls.cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_recordings (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                login_time TIMESTAMP,
                is_active INTEGER
            )
        """)
        
        cls.cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY,
                username TEXT,
                success INTEGER,
                timestamp TIMESTAMP
            )
        """)
        
        cls.cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY,
                event_type TEXT,
                severity TEXT,
                description TEXT,
                user_id INTEGER,
                timestamp TIMESTAMP
            )
        """)

        cls.conn.commit()
        cls.conn.close()
        
    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
            
    def setUp(self):
        self.ip_manager = IPManager(TEST_DB)
        self.rate_limiter = RateLimiter(TEST_DB)
        self.dashboard = MonitoringDashboard(TEST_DB)
        
    def test_ip_whitelist(self):
        ip = "192.168.1.100"
        
        # Add to whitelist
        res = self.ip_manager.add_to_whitelist(ip, "Test IP", "admin")
        self.assertTrue(res['success'])
        
        # Check if whitelisted
        self.assertTrue(self.ip_manager.is_whitelisted(ip))
        
        # Check access
        access = self.ip_manager.check_ip_access(ip)
        self.assertTrue(access['allowed'])
        self.assertTrue(access['whitelisted'])
        
        # Remove
        self.ip_manager.remove_from_whitelist(ip)
        self.assertFalse(self.ip_manager.is_whitelisted(ip))
        
    def test_ip_blacklist(self):
        ip = "10.0.0.5"
        
        # Add to blacklist
        res = self.ip_manager.add_to_blacklist(ip, "Bad IP", "admin")
        self.assertTrue(res['success'])
        
        # Check if blacklisted
        self.assertTrue(self.ip_manager.is_blacklisted(ip))
        
        # Check access (should be denied)
        access = self.ip_manager.check_ip_access(ip)
        self.assertFalse(access['allowed'])
        self.assertTrue(access['blacklisted'])
        
        # Remove
        self.ip_manager.remove_from_blacklist(ip)
        self.assertFalse(self.ip_manager.is_blacklisted(ip))
        
    def test_rate_limiter(self):
        resource = "api_test"
        identifier = "user_123"
        limit = 5
        window = 60
        
        # Reset first
        self.rate_limiter.reset_limit(resource, identifier)
        
        # Make requests
        for i in range(limit):
            res = self.rate_limiter.check_rate_limit(resource, identifier, limit, window)
            self.assertTrue(res['allowed'], f"Request {i+1} should be allowed")
            
        # Exceed limit
        res = self.rate_limiter.check_rate_limit(resource, identifier, limit, window)
        self.assertFalse(res['allowed'], "Request should be blocked")
        self.assertTrue(res['blocked'])
        
    def test_monitoring_dashboard(self):
        # Insert some dummy data
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO session_recordings (user_id, login_time, is_active) VALUES (1, datetime('now'), 1)")
        cursor.execute("INSERT INTO login_attempts (username, success, timestamp) VALUES ('admin', 0, datetime('now'))")
        conn.commit()
        conn.close()
        
        stats = self.dashboard.get_live_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('active_users', stats)
        self.assertIn('cpu_usage', stats)
        
        # We inserted 1 active user
        self.assertEqual(stats['active_users'], 1)
        
        # We inserted 1 failed login (but query is for last hour, so it should count)
        self.assertEqual(stats['failed_logins'], 1)

if __name__ == '__main__':
    unittest.main()
