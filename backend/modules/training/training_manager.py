import sqlite3
import json
import logging
from datetime import datetime

class TrainingManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Training Programs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_training_programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                training_type TEXT DEFAULT 'online', -- online, in_person
                content_url TEXT, -- Link to video or file
                duration_minutes INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Training Participants/Records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_training_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                training_id INTEGER NOT NULL,
                participant_name TEXT NOT NULL, -- Or employee_id if linked
                status TEXT DEFAULT 'assigned', -- assigned, completed, failed
                completion_date TEXT,
                score INTEGER,
                FOREIGN KEY (training_id) REFERENCES lms_training_programs (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_training_program(self, company_id, title, description, training_type, content_url, duration_minutes):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO lms_training_programs (company_id, title, description, training_type, content_url, duration_minutes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (company_id, title, description, training_type, content_url, duration_minutes))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error adding training program: {e}")
            return False
        finally:
            conn.close()

    def get_training_programs(self, company_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lms_training_programs WHERE company_id = ? ORDER BY created_at DESC', (company_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_training_record(self, company_id, training_id, participant_name, status='assigned', score=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            completion_date = datetime.now().strftime('%Y-%m-%d') if status == 'completed' else None
            cursor.execute('''
                INSERT INTO lms_training_records (company_id, training_id, participant_name, status, completion_date, score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (company_id, training_id, participant_name, status, completion_date, score))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error adding training record: {e}")
            return False
        finally:
            conn.close()

    def get_training_records(self, company_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, p.title as training_title 
            FROM lms_training_records r
            JOIN lms_training_programs p ON r.training_id = p.id
            WHERE r.company_id = ?
            ORDER BY r.completion_date DESC
        ''', (company_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_dashboard_stats(self, company_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total Programs
        cursor.execute('SELECT COUNT(*) FROM lms_training_programs WHERE company_id = ?', (company_id,))
        stats['total_programs'] = cursor.fetchone()[0]
        
        # Total Completed Trainings
        cursor.execute("SELECT COUNT(*) FROM lms_training_records WHERE company_id = ? AND status = 'completed'", (company_id,))
        stats['completed_trainings'] = cursor.fetchone()[0]
        
        # Total Participants (Unique)
        cursor.execute("SELECT COUNT(DISTINCT participant_name) FROM lms_training_records WHERE company_id = ?", (company_id,))
        stats['total_participants'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
