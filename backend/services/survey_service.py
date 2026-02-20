import json
import os
import logging
from typing import Dict, List, Optional
from backend.core.base_manager import BaseTenantManager

class SurveyService(BaseTenantManager):
    """
    LEGACY SERVICE - DEPRECATED
    Please use SurveyBuilder (backend/modules/surveys/survey_builder.py) instead.
    
    This service is maintained for backward compatibility but may not work with the current
    database schema (surveys, survey_questions tables have changed).
    """
    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        final_db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        super().__init__(final_db_path, company_id)
        logging.warning("SurveyService is deprecated. Use SurveyBuilder instead.")

    def create_tables(self) -> None:
        """Deprecated. Tables are managed by SurveyBuilder and migration scripts."""
        pass

    def create_survey(self, company_id: int, name: str, description: str = None, status: str = 'draft') -> int:
        """Deprecated. Use SurveyBuilder.insert('survey_templates', ...)"""
        logging.warning("SurveyService.create_survey is deprecated.")
        # Attempt to map to survey_templates
        try:
            self.set_company_context(company_id)
            return self.insert('survey_templates', {
                'name': name,
                'description': description,
                'is_active': 1 if status == 'active' else 0
            })
        except Exception as e:
            logging.error(f"Error in legacy create_survey: {e}")
            return -1

    def add_question(self, survey_id: int, text: str, q_type: str = 'text', options: Optional[List[str]] = None, required: bool = False, order_index: int = 0) -> int:
        """Deprecated. Use SurveyBuilder.insert('survey_questions', ...)"""
        logging.warning("SurveyService.add_question is deprecated.")
        try:
            # Map survey_id to template_id
            options_json = json.dumps(options or [])
            return self.insert('survey_questions', {
                'template_id': survey_id, # Assuming survey_id passed here corresponds to template_id
                'question_text': text,
                'question_type': q_type,
                'options': options_json,
                'is_required': 1 if required else 0,
                'display_order': order_index
            })
        except Exception as e:
            logging.error(f"Error in legacy add_question: {e}")
            return -1

    def submit_response(self, survey_id: int, user_id: int, company_id: int, answers: Dict[int, str]) -> int:
        """Deprecated. Use SurveyBuilder.submit_survey_response"""
        logging.warning("SurveyService.submit_response is deprecated.")
        # Logic is too different to map easily (SurveyBuilder needs user_survey_id)
        return -1

    def get_survey_with_questions(self, survey_id: int) -> Dict:
        """Deprecated."""
        return {}

    def get_results(self, survey_id: int) -> List[Dict]:
        """Deprecated."""
        return []
