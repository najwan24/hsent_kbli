#!/usr/bin/env python3
"""
Quick runner script for adding UUIDs to the dataset.
This is a convenience script that can be run from anywhere in the project.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the UUID generation script."""
    # Find the script directory
    current_dir = Path(__file__).parent
    uuid_script = current_dir / "02a_add_unique_ids.py"
    
    if not uuid_script.exists():
        print(f"❌ UUID script not found at {uuid_script}")
        return 1
    
    print("🔧 Running UUID generation script...")
    print("=" * 50)
    
    try:
        # Run the UUID script
        result = subprocess.run([sys.executable, str(uuid_script)], 
                              cwd=current_dir.parent)  # Run from project root
        
        if result.returncode == 0:
            print("\n✅ UUID generation completed successfully!")
            print("\n📋 Next steps:")
            print("1. Run pilot study: python src/03a_run_pilot_study.py")
            print("2. The script will automatically use mini_test_with_ids.csv")
        else:
            print("\n❌ UUID generation failed!")
            return result.returncode
            
    except Exception as e:
        print(f"\n❌ Error running UUID script: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
