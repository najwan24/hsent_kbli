"""
ACSES Pilot Study - Source Package
Core library for the ACSES pilot study pipeline
"""

# Main package exports for convenient access
from .api.gemini_client import GeminiClient
from .data.data_loader import DataLoader
from .pipeline.pilot_runner import PilotRunner
from .cli.arguments import create_pilot_study_parser, create_analysis_parser

__version__ = "1.0.0"

__all__ = [
    'GeminiClient',
    'DataLoader', 
    'PilotRunner',
    'create_pilot_study_parser',
    'create_analysis_parser',
    '__version__'
]

__version__ = "1.0.0"
__author__ = "ACSES Research Team"
