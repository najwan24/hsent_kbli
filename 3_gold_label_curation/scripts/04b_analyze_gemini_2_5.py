#!/usr/bin/env python3
"""
ACSES Pilot Study - Phase 4B: Analyze Gemini 2.5 Results (Refactored)
This script analyzes Gemini 2.5 Flash Lite results using consolidated src/ modules.

This is now a thin CLI wrapper that imports functionality from src/ modules.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
current_path = Path(__file__).parent.parent
sys.path.insert(0, str(current_path))

from src.analysis.results_analyzer import analyze_gemini_2_5_results
from src.utils.common import load_env_file, print_section_header


def main():
    """Main execution function using consolidated modules."""
    print_section_header("ACSES Pilot Study - Gemini 2.5 Analysis")
    
    # Load environment variables
    load_env_file()
    
    try:
        # Use the consolidated analysis function
        analyze_gemini_2_5_results()
        
        print(f"\n✅ Gemini 2.5 analysis completed!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
