#!/usr/bin/env python3
"""
ACSES Pilot Study - Phase 0: Setup and Validation (Refactored)
This script validates setup and runs quick tests using consolidated src/ modules.

This is now a thin CLI wrapper that imports functionality from src/ modules.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
current_path = Path(__file__).parent.parent
sys.path.insert(0, str(current_path))

from src.validation.setup_validator import SetupValidator
from src.processing.data_processor import CodebookProcessor
from src.utils.common import load_env_file


def main():
    """Main execution function using consolidated modules."""
    print("🚀 ACSES Pilot Study - Setup and Validation")
    print("=" * 60)
    
    # Load environment variables
    load_env_file()
    
    try:
        # Initialize validator
        validator = SetupValidator()
        
        # Run comprehensive validation
        results = validator.run_comprehensive_validation()
        
        # Run API test if basic validation passes
        if results["overall_status"] == "PASSED":
            print("\n🎯 RUNNING ADDITIONAL CHECKS")
            print("-" * 40)
            
            # Check if hierarchical codebook exists, create if needed
            codebook_processor = CodebookProcessor()
            hierarchical_path = codebook_processor.data_output_dir / "kbli_codebook_hierarchical.csv"
            
            if not hierarchical_path.exists():
                print("📚 Creating hierarchical codebook...")
                try:
                    codebook_processor.prepare_hierarchical_codebook(
                        "kbli_codebook.csv",
                        "kbli_codebook_hierarchical.csv"
                    )
                except Exception as e:
                    print(f"⚠️  Could not create hierarchical codebook: {e}")
                    print("   You may need to run: python scripts/01_prepare_codebook.py")
            else:
                print("✅ Hierarchical codebook already exists")
            
            # Run API connectivity test
            api_test_passed = validator.run_quick_test()
            
            if api_test_passed:
                print(f"\n🎉 SETUP COMPLETE!")
                print("✅ Environment validated")
                print("✅ Dependencies installed") 
                print("✅ API connectivity confirmed")
                print(f"\n💡 Next steps:")
                print("   1. python scripts/03a_run_pilot_study_refactored.py")
                print("   2. Check results in data/output/")
                return True
            else:
                print(f"\n⚠️  Setup mostly complete, but API test failed")
                print("   This might be due to network issues or API key problems.")
                return False
        else:
            print(f"\n❌ Setup validation failed!")
            print("   Please fix the issues above before proceeding.")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during setup validation: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
