#!/usr/bin/env python3
"""
ACSES Pilot Study - Phase 2A: Add Unique IDs (Refactored)
This script adds UUID identifiers to the test dataset using consolidated src/ modules.

This is now a thin CLI wrapper that imports functionality from src/ modules.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
current_path = Path(__file__).parent.parent
sys.path.insert(0, str(current_path))

from src.processing.data_processor import DataEnhancer
from src.utils.common import load_env_file, print_section_header


def main():
    """Main execution function using consolidated modules."""
    print_section_header("ACSES Pilot Study - Add Unique IDs")
    
    # Load environment variables  
    load_env_file()
    
    try:
        # Initialize data enhancer
        enhancer = DataEnhancer()
        
        print("🔢 Adding UUID identifiers to test dataset...")
        
        # Add UUIDs to the dataset
        enhanced_df = enhancer.add_uuids_to_dataset(
            input_file="mini_test.csv",
            output_file="mini_test_with_ids.csv"
        )
        
        # Validate the enhanced dataset
        print("\n🔍 Validating enhanced dataset...")
        is_valid = enhancer.validate_enhanced_dataset(enhanced_df)
        
        if is_valid:
            print("✅ Enhanced dataset validation passed!")
            
            # Create analysis
            print("\n📊 Creating dataset analysis...")
            enhancer.create_sample_analysis(enhanced_df)
            
            print(f"\n✅ UUID enhancement completed successfully!")
            print(f"📊 Enhanced dataset saved to: data/input/mini_test_with_ids.csv")
            print(f"📈 Analysis saved to: data/output/dataset_with_ids_analysis.json")
            
            print(f"\n💡 Next steps:")
            print("   1. python scripts/03a_run_pilot_study_refactored.py  # Run pilot study")
            print("   2. Check data/input/mini_test_with_ids.csv for the enhanced dataset")
            
            return True
        else:
            print("❌ Enhanced dataset validation failed!")
            return False
        
    except KeyboardInterrupt:
        print("\n⚠️ UUID enhancement interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during UUID enhancement: {e}")
        print(f"   Make sure data/input/mini_test.csv exists")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
