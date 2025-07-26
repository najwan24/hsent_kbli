"""
Consolidated Command Line Interface
Shared argument parsing for all scripts.
"""

import argparse
from typing import Dict, Any

from ..api.gemini_client import GeminiClient

# Default values
DEFAULT_MODEL_NAME = "models/gemini-2.5-flash-lite"
DEFAULT_DATASET = "mini_test_with_ids.csv"
DEFAULT_N_RUNS = 3
DEFAULT_TEMPERATURE = 0.7


def create_base_parser() -> argparse.ArgumentParser:
    """Create base argument parser with common arguments."""
    available_models = GeminiClient.get_available_models()
    
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Models:
""" + "\n".join([f"  {model}: {config['description']} ({config['rpm']} RPM)" 
                for model, config in available_models.items()])
    )
    
    return parser


def add_pilot_study_arguments(parser: argparse.ArgumentParser) -> None:
    """Add pilot study specific arguments."""
    available_models = GeminiClient.get_available_models()
    
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL_NAME,
        choices=list(available_models.keys()),
        help=f"Model to use for evaluation (default: {DEFAULT_MODEL_NAME})"
    )
    
    parser.add_argument(
        "--dataset", "-d",
        default=DEFAULT_DATASET,  
        help=f"Dataset filename in data/input/ directory (default: {DEFAULT_DATASET})"
    )
    
    parser.add_argument(
        "--runs", "-r",
        type=int,
        default=DEFAULT_N_RUNS,
        help=f"Number of runs per sample (default: {DEFAULT_N_RUNS})"
    )
    
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Temperature for generation (default: {DEFAULT_TEMPERATURE})"
    )
    
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: data/output/)"
    )


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add common arguments used across scripts."""
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit"
    )


def create_pilot_study_parser() -> argparse.ArgumentParser:
    """Create argument parser for pilot study scripts."""
    parser = create_base_parser()
    parser.description = "ACSES Pilot Study - Run LLM evaluation on KBLI code assignments"
    
    parser.epilog = """
Examples:
  python script.py
  python script.py --model models/gemini-1.5-flash-latest
  python script.py --dataset other_test.csv --model models/gemini-1.5-pro-latest
  python script.py --list-models

""" + parser.epilog
    
    add_pilot_study_arguments(parser)
    add_common_arguments(parser)
    
    return parser


def create_analysis_parser() -> argparse.ArgumentParser:
    """Create argument parser for analysis scripts."""
    parser = create_base_parser()
    parser.description = "ACSES Pilot Study - Analyze results from pilot studies"
    
    parser.add_argument(
        "--input-file", "-i",
        required=True,
        help="Input JSONL file to analyze"
    )
    
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for analysis results"
    )
    
    add_common_arguments(parser)
    
    return parser


def create_data_processing_parser() -> argparse.ArgumentParser:
    """Create argument parser for data processing scripts."""
    parser = create_base_parser()
    parser.description = "ACSES Pilot Study - Data processing utilities"
    
    parser.add_argument(
        "--input-file", "-i",
        help="Input file to process"
    )
    
    parser.add_argument(
        "--output-file", "-o",
        help="Output file path"
    )
    
    add_common_arguments(parser)
    
    return parser
