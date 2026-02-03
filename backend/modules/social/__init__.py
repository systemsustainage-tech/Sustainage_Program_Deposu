# Social Modules
from .diversity_manager import DiversityManager
from .hr_manager import HRManager
from .safety_manager import SafetyManager
# from .social_dashboard_gui import SocialDashboardGUI
from .training_manager import TrainingManager


# Alias sınıflar - main_app.py ile uyumluluk için
class HRMetrics(HRManager):
    """HRManager için alias"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_workforce_summary(self, company_id: int, year: int) -> dict:
        """İş gücü özeti"""
        try:
            return self.get_hr_summary(company_id, year)
        except Exception:
            # Return empty/zero data instead of fake numbers
            return {'total_employees': 0, 'female_percentage': 0}

class OHSMetrics(SafetyManager):
    """SafetyManager için alias"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_summary(self, company_id: int, year: int) -> dict:
        """İSG özeti"""
        try:
            return self.get_safety_summary(company_id, year)
        except Exception:
            return {'total_incidents': 0, 'ltifr': 0.0}

class TrainingMetrics(TrainingManager):
    """TrainingManager için alias"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_summary(self, company_id: int, year: int) -> dict:
        """Eğitim özeti"""
        try:
            return self.get_training_summary(company_id, year)
        except Exception:
            return {'total_hours': 0, 'completion_rate': 0}

__all__ = [
    'HRManager', 'HRMetrics',
    'SafetyManager', 'OHSMetrics',
    'TrainingManager', 'TrainingMetrics',
    'DiversityManager'
]
