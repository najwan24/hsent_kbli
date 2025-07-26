#!/usr/bin/env python3
"""
ACSES Pilot Study - Phase 1: Codebook Preparation (Refactored)
This script transforms the KBLI codebook into hierarchical format using consolidated src/ modules.

This is now a thin CLI wrapper that imports functionality from src/ modules.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
current_path = Path(__file__).parent.parent
sys.path.insert(0, str(current_path))

from src.processing.data_processor import CodebookProcessor
from src.utils.common import load_env_file, print_section_header


def main():
    """Main execution function using consolidated modules."""
    print_section_header("ACSES Pilot Study - Codebook Preparation")
    
    # Load environment variables
    load_env_file()
    
    try:
        # Initialize codebook processor
        processor = CodebookProcessor()
        
        print("🔄 Transforming KBLI codebook to hierarchical format...")
        
        # Process the codebook
        processor.prepare_hierarchical_codebook(
            input_file="kbli_codebook.csv",
            output_file="kbli_codebook_hierarchical.csv"
        )
        
        print(f"\n✅ Codebook preparation completed successfully!")
        print(f"📊 Hierarchical codebook saved to: data/output/kbli_codebook_hierarchical.csv")
        
        print(f"\n💡 Next steps:")
        print("   1. python scripts/02a_add_unique_ids.py  # Add UUIDs to test data")
        print("   2. python scripts/03a_run_pilot_study_refactored.py  # Run pilot study")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ Codebook preparation interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during codebook preparation: {e}")
        print(f"   Make sure data/input/kbli_codebook.csv exists")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
