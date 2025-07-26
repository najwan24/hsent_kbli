"""
Common utilities for ACSES Pilot Study
Shared functions used across the pipeline
"""
import os
import json
import logging
import uuid
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

def setup_logging(name: str, level: str = "INFO", log_dir: Optional[Path] = None) -> logging.Logger:
    """Setup consistent logging across modules"""
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler (optional)
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / f"{name}.log")
        file_handler.setLevel(logging.DEBUG)
        
        # Detailed format for file logs
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Simple format for console
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

def generate_uuid() -> str:
    """Generate UUID4 string for unique identification"""
    return str(uuid.uuid4())

def save_jsonl_record(record: Dict[str, Any], filepath: Path) -> bool:
    """
    Save a single record to JSONL file (append mode)
    
    Args:
        record: Dictionary to save as JSON line
        filepath: Path to JSONL file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Append the record as a new line
        with open(filepath, 'a', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, default=str)
            f.write('\n')
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving to {filepath}: {e}")
        return False

def load_jsonl_records(filepath: Path) -> List[Dict[str, Any]]:
    """
    Load all records from JSONL file
    
    Args:
        filepath: Path to JSONL file
        
    Returns:
        List of dictionaries from JSONL file
    """
    records = []
    
    if not filepath.exists():
        return records
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        record = json.loads(line)
                        records.append(record)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Warning: Invalid JSON on line {line_num} in {filepath.name}: {e}")
                        continue
    
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
    
    return records

def validate_required_files(paths: List[Path]) -> Tuple[bool, List[str]]:
    """
    Validate that required files exist
    
    Args:
        paths: List of file paths to check
        
    Returns:
        Tuple of (all_exist: bool, missing_files: List[str])
    """
    missing = []
    
    for path in paths:
        if not path.exists():
            missing.append(str(path))
    
    return len(missing) == 0, missing

def load_csv_with_dtype(filepath: Path, dtype_dict: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Load CSV file with proper data types
    
    Args:
        filepath: Path to CSV file
        dtype_dict: Dictionary mapping column names to data types
        
    Returns:
        Loaded DataFrame
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Default dtype for common columns
    default_dtype = {
        'kbli_code': str,
        'sample_id': str,
        'code_5': str,
        'code_4': str,
        'code_3': str,
        'code_2': str,
        'code_1': str,
        'kode': str
    }
    
    if dtype_dict:
        default_dtype.update(dtype_dict)
    
    return pd.read_csv(filepath, dtype=default_dtype)

def create_timestamp() -> str:
    """Create ISO format timestamp string"""
    return datetime.now().isoformat()

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def print_section_header(title: str, width: int = 60) -> None:
    """Print a formatted section header"""
    print(f"\n{title}")
    print("=" * width)

def print_progress(current: int, total: int, prefix: str = "Progress") -> None:
    """Print progress information"""
    percentage = (current / total) * 100 if total > 0 else 0
    print(f"{prefix}: {current}/{total} ({percentage:.1f}%)")

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    return numerator / denominator if denominator != 0 else default

def extract_error_info(exception: Exception) -> Tuple[str, str]:
    """
    Extract error type and message from exception
    
    Args:
        exception: The exception to analyze
        
    Returns:
        Tuple of (error_type, error_message)
    """
    error_type = type(exception).__name__
    error_message = str(exception)
    
    # Truncate very long error messages
    if len(error_message) > 200:
        error_message = error_message[:200] + "..."
    
    return error_type, error_message

class ProgressTracker:
    """Simple progress tracking utility"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        self._print_progress()
    
    def set_current(self, current: int):
        """Set current progress"""
        self.current = current
        self._print_progress()
    
    def _print_progress(self):
        """Print current progress"""
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        if self.current > 0:
            eta_seconds = (elapsed / self.current) * (self.total - self.current)
            eta_str = f", ETA: {format_duration(eta_seconds)}"
        else:
            eta_str = ""
        
        print(f"\r{self.description}: {self.current}/{self.total} ({percentage:.1f}%{eta_str})", end="", flush=True)
        
        if self.current >= self.total:
            print()  # New line when complete
