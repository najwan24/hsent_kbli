#!/usr/bin/env python3
"""
ACSES Pilot Study - Phase 4A: Analyze Results (Refactored)
This script analyzes pilot study results using consolidated src/ modules.

This is now a thin CLI wrapper that imports functionality from src/ modules.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
current_path = Path(__file__).parent.parent
sys.path.insert(0, str(current_path))

from src.analysis.results_analyzer import ResultsAnalyzer
from src.utils.common import load_env_file, print_section_header


def main():
    """Main execution function using consolidated modules."""
    print_section_header("ACSES Pilot Study - Results Analysis")
    
    # Load environment variables
    load_env_file()
    
    try:
        # Initialize results analyzer
        analyzer = ResultsAnalyzer()
        
        # Define models to analyze
        models_to_analyze = [
            "gemini_1.5_flash_latest",
            "gemini_1.5_pro_latest", 
            "gemini_2.5_flash_lite"
        ]
        
        print("🔍 Analyzing pilot study results...")
        
        successful_analyses = []
        
        for model in models_to_analyze:
            print(f"\n📊 Analyzing {model}...")
            try:
                analysis = analyzer.analyze_model_results(model)
                
                if "error" not in analysis:
                    analyzer.print_analysis_report(analysis)
                    successful_analyses.append((model, analysis))
                else:
                    print(f"⚠️  {analysis['error']}")
                    
            except Exception as e:
                print(f"❌ Error analyzing {model}: {e}")
        
        # Model comparison if multiple successful analyses
        if len(successful_analyses) > 1:
            print(f"\n🆚 MODEL COMPARISON")
            print("=" * 60)
            
            comparison = analyzer.compare_models([model for model, _ in successful_analyses])
            
            if "error" not in comparison.get("summary", {}):
                summary = comparison["summary"]
                print(f"🏆 Best performing model: {summary['best_model']}")
                print(f"📈 Best success rate: {summary['best_success_rate']:.1%}")
                print(f"📊 Models compared: {summary['models_compared']}")
                print(f"🔢 Total samples processed: {summary['total_samples_processed']}")
            
        elif len(successful_analyses) == 1:
            model, analysis = successful_analyses[0]
            print(f"\n💡 Only {model} results found.")
            print("   Run pilot studies for other models to enable comparison.")
        
        else:
            print(f"\n❌ No valid results found for analysis.")
            print("   Make sure pilot studies have been completed.")
            print("   Check data/output/ directory for .jsonl result files.")
            return False
        
        print(f"\n✅ Results analysis completed!")
        
        if successful_analyses:
            print(f"\n💡 Next steps:")
            print("   1. Review the analysis above")
            print("   2. Check individual .jsonl files in data/output/")
            print("   3. Use notebooks/analyze_pilot.ipynb for detailed analysis")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ Results analysis interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during results analysis: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
