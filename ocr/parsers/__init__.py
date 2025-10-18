# ocr/parsers/__init__.py
# This file makes the parsers directory a Python package

from .lab_report_parser import LabReportParser
from .discharge_parser import DischargeSummaryParser
from .clinic_notes_parser import ClinicNotesParser
from .fallback_parser import GeneralMedicalParser

__all__ = [
    'LabReportParser',
    'DischargeSummaryParser', 
    'ClinicNotesParser',
    'GeneralMedicalParser'
]