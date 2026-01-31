# IIRC Reports Module
from .capitals_report import CapitalsReportGenerator
from .integrated_report import IntegratedReportGenerator
from .value_creation_report import ValueCreationReportGenerator

__all__ = [
    'IntegratedReportGenerator',
    'CapitalsReportGenerator',
    'ValueCreationReportGenerator'
]

