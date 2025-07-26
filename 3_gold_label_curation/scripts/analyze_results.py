#!/usr/bin/env python3
"""Script to analyze pilot study results."""

import argparse
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis.results_analyzer import ResultsAnalyzer


def main():
    parser = argparse.ArgumentParser(description="Analyze pilot study results")
    parser.add_argument(
        "--model", 
        default="gemini_2.5_flash_lite",
        help="Model name to analyze (default: gemini_2.5_flash_lite)"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Project root directory (defaults to script's grandparent)"
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = ResultsAnalyzer(args.project_root)
        analysis = analyzer.analyze_model_results(args.model)
        analyzer.print_analysis_report(analysis)
        
        # Additional guidance
        if analysis.get('incomplete_samples', 0) > 0:
            print(f"\n💡 NEXT STEPS:")
            print("1. The rate limiting fix has been applied")
            print("2. Run the pilot script again with proper delays")
            print("3. It will automatically retry failed runs only")
            print("4. Expected time with fix: ~3 minutes for remaining samples")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
