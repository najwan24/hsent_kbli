"""
Utility functions to convert JSON pilot results to JSONL format.
This helps if you have existing JSON results and want to convert them.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

from .common import setup_logging

logger = setup_logging(__name__)

def convert_json_to_jsonl(json_path: str, jsonl_path: str) -> bool:
    """
    Convert a JSON array file to JSONL format.
    
    Args:
        json_path: Path to the input JSON file
        jsonl_path: Path to the output JSONL file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🔄 Converting {json_path} to {jsonl_path}")
        
        # Load JSON array
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print(f"❌ Error: JSON file does not contain an array")
            return False
        
        # Write as JSONL
        os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for item in data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        
        print(f"✅ Successfully converted {len(data)} records")
        return True
        
    except Exception as e:
        print(f"❌ Error converting file: {e}")
        return False

def load_jsonl_as_list(jsonl_path: str) -> list:
    """
    Load JSONL file and return as list (for backward compatibility).
    
    Args:
        jsonl_path: Path to JSONL file
        
    Returns:
        List of dictionaries
    """
    results = []
    
    if not os.path.exists(jsonl_path):
        return results
    
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        result = json.loads(line)
                        results.append(result)
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Warning: Invalid JSON on line {line_num}: {e}")
                        continue
        
        print(f"📂 Loaded {len(results)} results from {jsonl_path}")
        
    except Exception as e:
        print(f"❌ Error loading JSONL file: {e}")
    
    return results

def main():
    """Main function to handle conversion."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / "data" / "output"
    
    # Find JSON files to convert
    json_files = list(output_dir.glob("pilot_results_*.json"))
    
    if not json_files:
        print("ℹ️  No JSON pilot result files found to convert.")
        return
    
    print(f"🔍 Found {len(json_files)} JSON files to convert:")
    for json_file in json_files:
        print(f"  - {json_file.name}")
    
    # Convert each file
    converted_count = 0
    
    for json_path in json_files:
        # Create JSONL filename
        jsonl_name = json_path.stem + ".jsonl"
        jsonl_path = output_dir / jsonl_name
        
        # Skip if JSONL already exists and is newer
        if jsonl_path.exists() and jsonl_path.stat().st_mtime > json_path.stat().st_mtime:
            print(f"⏭️  Skipping {json_path.name} (JSONL is newer)")
            continue
        
        # Convert
        if convert_json_to_jsonl(str(json_path), str(jsonl_path)):
            converted_count += 1
            
            # Optionally backup the original JSON
            backup_name = json_path.stem + "_backup.json"
            backup_path = output_dir / backup_name
            
            if not backup_path.exists():
                try:
                    json_path.rename(backup_path)
                    print(f"📦 Original JSON backed up as {backup_name}")
                except Exception as e:
                    print(f"⚠️  Could not backup original: {e}")
    
    print(f"\n🎉 Conversion complete! {converted_count} files converted.")
    
    if converted_count > 0:
        print(f"\n💡 Your analysis notebook will now work with JSONL files.")
        print(f"💡 Original JSON files have been backed up with '_backup' suffix.")

if __name__ == "__main__":
    main()
