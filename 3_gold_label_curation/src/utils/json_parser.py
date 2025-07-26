"""
Consolidated JSON Processing Utilities
Handles JSON extraction, parsing, and JSONL file operations.
"""

import json
import re
import os
from typing import Dict, Any, List, Tuple, Set, Optional
from datetime import datetime


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from API response text.
    
    Args:
        text: Raw response text from the API
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        ValueError: If no valid JSON found or parsing fails
    """
    # Try to find JSON block marked with ```json
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find any JSON object in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            raise ValueError(f"No JSON found in response: {text[:200]}...")
    
    # Parse the JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}\nJSON string: {json_str[:200]}...")


def save_result_to_jsonl(result: Dict[str, Any], output_path: str) -> bool:
    """
    Append a single result to JSONL file immediately.
    
    Args:
        result: Result dictionary to save
        output_path: Path to JSONL file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'a', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
            f.write('\n')
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not save result: {e}")
        return False


def load_existing_results(output_path: str) -> Tuple[List[Dict[str, Any]], Set[Tuple[str, int]]]:
    """
    Load existing results from JSONL file to enable resumption.
    
    Args:
        output_path: Path to the JSONL results file
        
    Returns:
        Tuple of (list of existing results, set of completed sample_run combinations)
    """
    existing_results = []
    completed_runs = set()
    
    if not os.path.exists(output_path):
        return existing_results, completed_runs
    
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        result = json.loads(line)
                        existing_results.append(result)
                        
                        # Create unique key for sample_id + run_number
                        sample_id = result.get('sample_id', -1)
                        run_num = result.get('run_number', -1)
                        
                        # Only mark as completed if it was successful
                        if result.get('success', False):
                            completed_runs.add((sample_id, run_num))
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Warning: Invalid JSON on line {line_num}: {e}")
                        continue
        
        print(f"📂 Found {len(existing_results)} existing results")
        
        # Count successful vs failed results
        successful_runs = sum(1 for r in existing_results if r.get('success', False))
        failed_runs = len(existing_results) - successful_runs
        
        print(f"📊 Completed runs: {len(completed_runs)} successful, {failed_runs} failed")
        print(f"🔄 Failed runs will be retried on resume")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not load existing results: {e}")
        return [], set()
    
    return existing_results, completed_runs


def calculate_success_rate(output_path: str) -> float:
    """
    Calculate success rate from a JSONL results file.
    
    Args:
        output_path: Path to the JSONL results file
        
    Returns:
        Success rate as a float between 0 and 1
    """
    if not os.path.exists(output_path):
        return 0.0
    
    successful_count = 0
    total_count = 0
    
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        result = json.loads(line)
                        total_count += 1
                        if result.get('success', False):
                            successful_count += 1
                    except json.JSONDecodeError:
                        continue
        
        return successful_count / total_count if total_count > 0 else 0.0
        
    except Exception as e:
        print(f"⚠️  Warning: Could not calculate success rate: {e}")
        return 0.0


def validate_jsonl_file(file_path: str) -> Dict[str, Any]:
    """
    Validate a JSONL file and return statistics.
    
    Args:
        file_path: Path to the JSONL file
        
    Returns:
        Dictionary with validation statistics
    """
    stats = {
        'total_lines': 0,
        'valid_json_lines': 0,
        'invalid_json_lines': 0,
        'empty_lines': 0,
        'successful_results': 0,
        'failed_results': 0,
        'unique_samples': set(),
        'errors': []
    }
    
    if not os.path.exists(file_path):
        stats['errors'].append(f"File not found: {file_path}")
        return stats
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                stats['total_lines'] += 1
                
                if not line.strip():
                    stats['empty_lines'] += 1
                    continue
                
                try:
                    result = json.loads(line.strip())
                    stats['valid_json_lines'] += 1
                    
                    # Track success/failure
                    if result.get('success', False):
                        stats['successful_results'] += 1
                    else:
                        stats['failed_results'] += 1
                    
                    # Track unique samples
                    sample_id = result.get('sample_id')
                    if sample_id:
                        stats['unique_samples'].add(sample_id)
                        
                except json.JSONDecodeError as e:
                    stats['invalid_json_lines'] += 1
                    stats['errors'].append(f"Line {line_num}: {str(e)}")
    
    except Exception as e:
        stats['errors'].append(f"Error reading file: {str(e)}")
    
    # Convert set to count for JSON serialization
    stats['unique_sample_count'] = len(stats['unique_samples'])
    del stats['unique_samples']
    
    return stats
