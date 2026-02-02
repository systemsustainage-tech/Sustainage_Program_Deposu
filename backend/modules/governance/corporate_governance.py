#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kurumsal Yönetim Modülü
Yönetim kurulu, komiteler ve yönetişim yapısı
"""

import logging
import os
import sqlite3
from typing import Dict, List
from config.database import DB_PATH


class CorporateGovernanceManager:
    """Kurumsal yönetim ve yönetişim yapısı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Kurumsal yönetim tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS board_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    member_name TEXT NOT NULL,
                    position TEXT NOT NULL,
                    member_type TEXT NOT NULL,
                    appointment_date TEXT,
                    term_end_date TEXT,
                    independence_status TEXT,
                    expertise_area TEXT,
                    gender TEXT,
                    age INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS governance_committees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    committee_name TEXT NOT NULL,
                    committee_type TEXT NOT NULL,
                    chair_person TEXT,
                    member_count INTEGER,
                    meeting_frequency TEXT,
                    responsibilities TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS governance_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    policy_name TEXT NOT NULL,
                    policy_type TEXT NOT NULL,
                    version TEXT,
                    effective_date TEXT,
                    review_date TEXT,
                    approval_authority TEXT,
                    compliance_requirements TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ethics_compliance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    training_name TEXT,
                    participants INTEGER,
                    total_hours REAL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fair_operating_practices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    practice_area TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    description TEXT,
                    date DATE,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Kurumsal yonetim modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Kurumsal yonetim modulu tablo olusturma: {e}")
            
    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        stats = {
            'board_members': 0,
            'committees': 0,
            'policies': 0,
            'compliance_rate': 0
        }
        
        try:
            # Yönetim kurulu üye sayısı
            cursor.execute("SELECT COUNT(*) FROM board_members WHERE company_id = ? AND status = 'active'", (company_id,))
            row = cursor.fetchone()
            if row:
                stats['board_members'] = row[0]
                
            # Komite sayısı
            cursor.execute("SELECT COUNT(*) FROM governance_committees WHERE company_id = ? AND status = 'active'", (company_id,))
            row = cursor.fetchone()
            if row:
                stats['committees'] = row[0]
                
            # Politika sayısı
            cursor.execute("SELECT COUNT(*) FROM governance_policies WHERE company_id = ? AND status = 'active'", (company_id,))
            row = cursor.fetchone()
            if row:
                stats['policies'] = row[0]
                
            # Uyum oranı (örnek: politikaların % kaçı güncel) - şimdilik dummy
            if stats['policies'] > 0:
                stats['compliance_rate'] = 100
                
        except Exception as e:
            logging.error(f"Governance stats error: {e}")
        finally:
            conn.close()
            
        return stats

    def add_board_member(self, company_id: int, member_name: str, position: str,
                        member_type: str, appointment_date: str = None,
                        term_end_date: str = None, independence_status: str = None,
                        expertise_area: str = None, gender: str = None, age: int = None) -> bool:
        """Yönetim kurulu üyesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO board_members 
                (company_id, member_name, position, member_type, appointment_date,
                 term_end_date, independence_status, expertise_area, gender, age)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, member_name, position, member_type, appointment_date,
                  term_end_date, independence_status, expertise_area, gender, age))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Yönetim kurulu üyesi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_governance_committee(self, company_id: int, committee_name: str, committee_type: str,
                               chair_person: str = None, member_count: int = None,
                               meeting_frequency: str = None, responsibilities: str = None) -> bool:
        """Yönetişim komitesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO governance_committees 
                (company_id, committee_name, committee_type, chair_person,
                 member_count, meeting_frequency, responsibilities)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, committee_name, committee_type, chair_person,
                  member_count, meeting_frequency, responsibilities))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Yönetişim komitesi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_governance_policy(self, company_id: int, policy_name: str, policy_type: str,
                            version: str = None, effective_date: str = None,
                            review_date: str = None, approval_authority: str = None,
                            compliance_requirements: str = None) -> bool:
        """Yönetişim politikası ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO governance_policies 
                (company_id, policy_name, policy_type, version, effective_date,
                 review_date, approval_authority, compliance_requirements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, policy_name, policy_type, version, effective_date,
                  review_date, approval_authority, compliance_requirements))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Yönetişim politikası ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_ethics_training(self, company_id: int, training_name: str, participants: int,
                          total_hours: float, description: str = None) -> bool:
        """Etik eğitim/uyum kaydı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO ethics_compliance 
                (company_id, training_name, participants, total_hours, description)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, training_name, participants, total_hours, description))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Etik eğitim ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict[str, int]:
        """Dashboard için özet istatistikler"""
        stats = {'board_members': 0, 'committees': 0, 'ethics_training': 0}
        conn = sqlite3.connect(self.db_path)
        try:
            # Board Members
            row = conn.execute("SELECT COUNT(*) FROM board_members WHERE company_id = ? AND status = 'active'", (company_id,)).fetchone()
            if row: stats['board_members'] = row[0]
            
            # Committees
            row = conn.execute("SELECT COUNT(*) FROM governance_committees WHERE company_id = ? AND status = 'active'", (company_id,)).fetchone()
            if row: stats['committees'] = row[0]
            
            # Ethics
            row = conn.execute("SELECT COUNT(*) FROM ethics_compliance WHERE company_id = ?", (company_id,)).fetchone()
            if row: stats['ethics_training'] = row[0]
            
        except Exception as e:
            logging.error(f"Error in get_stats: {e}")
        finally:
            conn.close()
        return stats

    def get_stats(self, company_id: int) -> Dict:
        """Alias for get_dashboard_stats"""
        return self.get_dashboard_stats(company_id)


    def get_recent_data(self, company_id: int, limit: int = 10) -> list:
        """Son aktiviteleri getir"""
        recent_data = []
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            # Board
            rows = conn.execute("SELECT 'board' as type, member_name || ' (' || position || ')' as detail, created_at as date FROM board_members WHERE company_id = ? ORDER BY created_at DESC LIMIT ?", (company_id, limit)).fetchall()
            for r in rows: recent_data.append(dict(r))
            
            # Committee
            rows = conn.execute("SELECT 'committee' as type, committee_name as detail, created_at as date FROM governance_committees WHERE company_id = ? ORDER BY created_at DESC LIMIT ?", (company_id, limit)).fetchall()
            for r in rows: recent_data.append(dict(r))
            
            # Ethics
            rows = conn.execute("SELECT 'ethics' as type, training_name as detail, created_at as date FROM ethics_compliance WHERE company_id = ? ORDER BY created_at DESC LIMIT ?", (company_id, limit)).fetchall()
            for r in rows: recent_data.append(dict(r))
            
            recent_data.sort(key=lambda x: x['date'], reverse=True)
            recent_data = recent_data[:limit]
            
        except Exception as e:
            logging.error(f"Error in get_recent_data: {e}")
        finally:
            conn.close()
            
        return recent_data

    def get_recent_records(self, company_id: int, limit: int = 5) -> list:
        """Son eklenen yönetişim verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        recent_data = []

        try:
            cursor.execute("""
                SELECT id, member_name as detail, 'board' as type, created_at 
                FROM board_members 
                WHERE company_id = ? 
                UNION ALL
                SELECT id, committee_name as detail, 'committee' as type, created_at
                FROM governance_committees
                WHERE company_id = ?
                UNION ALL
                SELECT id, training_name as detail, 'ethics' as type, created_at
                FROM ethics_compliance
                WHERE company_id = ?
                ORDER BY created_at DESC LIMIT ?
            """, (company_id, company_id, company_id, limit))
            
            rows = cursor.fetchall()
            for row in rows:
                recent_data.append({
                    'id': row['id'],
                    'detail': row['detail'],
                    'type': row['type'],
                    'created_at': row['created_at']
                })
                
        except Exception as e:
            logging.error(f"Yönetişim geçmiş veri getirme hatası: {e}")
        finally:
            conn.close()

        return recent_data

    def get_governance_summary(self, company_id: int) -> Dict:
        """Yönetişim özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Yönetim kurulu kompozisyonu
            cursor.execute("""
                SELECT member_type, gender, independence_status, COUNT(*)
                FROM board_members 
                WHERE company_id = ? AND status = 'active'
                GROUP BY member_type, gender, independence_status
            """, (company_id,))

            board_composition = {}
            total_members = 0
            independent_members = 0
            female_members = 0

            for row in cursor.fetchall():
                member_type, gender, independence, count = row
                if member_type not in board_composition:
                    board_composition[member_type] = {}
                if gender not in board_composition[member_type]:
                    board_composition[member_type][gender] = 0
                board_composition[member_type][gender] += count

                total_members += count
                if independence == 'Independent':
                    independent_members += count
                if gender == 'Female':
                    female_members += count

            # Komiteler
            cursor.execute("""
                SELECT committee_type, COUNT(*), AVG(member_count)
                FROM governance_committees 
                WHERE company_id = ? AND status = 'active'
                GROUP BY committee_type
            """, (company_id,))

            committees = {}
            total_committees = 0
            for row in cursor.fetchall():
                committee_type, count, avg_members = row
                committees[committee_type] = {
                    'count': count,
                    'average_members': avg_members
                }
                total_committees += count

            # Politikalar
            cursor.execute("""
                SELECT policy_type, COUNT(*)
                FROM governance_policies 
                WHERE company_id = ? AND status = 'active'
                GROUP BY policy_type
            """, (company_id,))

            policies = {}
            total_policies = 0
            for row in cursor.fetchall():
                policy_type, count = row
                policies[policy_type] = count
                total_policies += count

            # Yönetişim metrikleri
            independence_ratio = (independent_members / total_members * 100) if total_members > 0 else 0
            gender_diversity_ratio = (female_members / total_members * 100) if total_members > 0 else 0

            return {
                'board_composition': board_composition,
                'total_board_members': total_members,
                'independent_members': independent_members,
                'female_members': female_members,
                'independence_ratio': independence_ratio,
                'gender_diversity_ratio': gender_diversity_ratio,
                'committees': committees,
                'total_committees': total_committees,
                'policies': policies,
                'total_policies': total_policies,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"Yönetişim özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()

    def add_fair_operating_record(self, company_id: int, data: Dict) -> bool:
        """Adil çalışma uygulaması kaydı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO fair_operating_practices 
                (company_id, practice_area, activity_type, description, date)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, data.get('practice_area'), data.get('activity_type'), 
                  data.get('description'), data.get('date')))
            
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Fair operating record add error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_fair_operating_records(self, company_id: int) -> List[Dict]:
        """Adil çalışma kayıtlarını getir"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        records = []
        
        try:
            rows = conn.execute("""
                SELECT * FROM fair_operating_practices 
                WHERE company_id = ? AND status = 'active' 
                ORDER BY date DESC
            """, (company_id,)).fetchall()
            
            for row in rows:
                records.append(dict(row))
        except Exception as e:
            logging.error(f"Fair operating records error: {e}")
        finally:
            conn.close()
            
        return records

    def get_fair_operating_stats(self, company_id: int) -> Dict:
        """Adil çalışma istatistikleri"""
        stats = {
            'total_practices': 0,
            'anti_corruption': 0,
            'fair_competition': 0,
            'value_chain': 0
        }
        
        conn = sqlite3.connect(self.db_path)
        try:
            # Total
            row = conn.execute("SELECT COUNT(*) FROM fair_operating_practices WHERE company_id = ? AND status = 'active'", (company_id,)).fetchone()
            if row: stats['total_practices'] = row[0]
            
            # Anti-corruption
            row = conn.execute("SELECT COUNT(*) FROM fair_operating_practices WHERE company_id = ? AND practice_area = 'Anti-corruption' AND status = 'active'", (company_id,)).fetchone()
            if row: stats['anti_corruption'] = row[0]
            
            # Fair Competition
            row = conn.execute("SELECT COUNT(*) FROM fair_operating_practices WHERE company_id = ? AND practice_area = 'Fair Competition' AND status = 'active'", (company_id,)).fetchone()
            if row: stats['fair_competition'] = row[0]

            # Value Chain
            row = conn.execute("SELECT COUNT(*) FROM fair_operating_practices WHERE company_id = ? AND practice_area = 'Value Chain' AND status = 'active'", (company_id,)).fetchone()
            if row: stats['value_chain'] = row[0]
            
        except Exception as e:
            logging.error(f"Fair operating stats error: {e}")
        finally:
            conn.close()
            
        return stats
