# ocr/utils/__init__.py
# This file makes the utils directory a Python package

from .data_validator import DataValidator
from .document_classifier import DocumentClassifier

__all__ = [
    'DataValidator',
    'DocumentClassifier'
]