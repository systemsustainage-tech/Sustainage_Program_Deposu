import logging
from datetime import datetime
from typing import List, Dict, Optional
from backend.core.base_manager import BaseTenantManager

class TrainingManager(BaseTenantManager):
    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._init_tables()

    def _init_tables(self):
        # Training Programs table
        self.execute_update('''
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
        self.execute_update('''
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

    def add_training_program(self, company_id, title, description, training_type, content_url, duration_minutes):
        try:
            self.execute_update('''
                INSERT INTO lms_training_programs (company_id, title, description, training_type, content_url, duration_minutes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (company_id, title, description, training_type, content_url, duration_minutes), company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Error adding training program: {e}")
            return False

    def get_training_programs(self, company_id) -> List[Dict]:
        rows = self.execute_query('SELECT * FROM lms_training_programs WHERE company_id = ? ORDER BY created_at DESC', (company_id,), company_id=company_id)
        return rows

    def add_training_record(self, company_id, training_id, participant_name, status='assigned', score=None):
        try:
            completion_date = datetime.now().strftime('%Y-%m-%d') if status == 'completed' else None
            self.execute_update('''
                INSERT INTO lms_training_records (company_id, training_id, participant_name, status, completion_date, score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (company_id, training_id, participant_name, status, completion_date, score), company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Error adding training record: {e}")
            return False

    def get_training_records(self, company_id) -> List[Dict]:
        rows = self.execute_query('''
            SELECT r.*, p.title as training_title 
            FROM lms_training_records r
            JOIN lms_training_programs p ON r.training_id = p.id
            WHERE r.company_id = ?
            ORDER BY r.completion_date DESC
        ''', (company_id,), company_id=company_id)
        return rows
