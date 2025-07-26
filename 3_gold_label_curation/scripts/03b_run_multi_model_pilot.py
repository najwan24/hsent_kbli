#!/usr/bin/env python3
"""
ACSES Pilot Study - Phase 3B: Multi-Model Pilot (Refactored)
This script runs pilot studies for multiple models using consolidated src/ modules.

This is now a thin CLI wrapper that imports functionality from src/ modules.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
current_path = Path(__file__).parent.parent
sys.path.insert(0, str(current_path))

from src.utils.common import load_env_file, print_section_header
from src.api.gemini_client import GeminiClient


def run_pilot_for_model(model_name: str) -> bool:
    """
    Run pilot study for a specific model.
    
    Args:
        model_name: Name of the model to test
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n🤖 Running pilot for: {model_name}")
    print("-" * 50)
    
    try:
        # Get the path to the pilot script
        script_path = Path(__file__).parent / "03a_run_pilot_study_refactored.py"
        
        # Run the pilot script with the specific model
        result = subprocess.run([
            sys.executable, 
            str(script_path),
            "--model", model_name,
            "--verbose"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {model_name}: Pilot completed successfully")
            return True
        else:
            print(f"❌ {model_name}: Pilot failed")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {model_name}: Error running pilot - {e}")
        return False


def main():
    """Main execution function using consolidated modules."""
    print_section_header("ACSES Pilot Study - Multi-Model Comparison")
    
    # Load environment variables
    load_env_file()
    
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize Gemini client to check available models
        client = GeminiClient()
        available_models = client.list_available_models()
        
        # Models to test (can be configured)
        models_to_test = [
            "models/gemini-1.5-flash-latest",
            "models/gemini-1.5-pro-latest", 
            "models/gemini-2.5-flash-lite"
        ]
        
        # Filter to only test available models
        valid_models = [m for m in models_to_test if m in available_models]
        
        if not valid_models:
            print("❌ No valid models found to test!")
            return False
        
        print(f"🤖 Models to test: {', '.join([m.split('/')[-1] for m in valid_models])}")
        
        # Check prerequisites
        required_files = [
            Path(__file__).parent.parent / "data" / "input" / "kbli_codebook_hierarchical.csv",
            Path(__file__).parent.parent / "data" / "input" / "mini_test_with_ids.csv",
            Path(__file__).parent.parent / "prompts" / "master_prompt.txt"
        ]
        
        missing_files = [f for f in required_files if not f.exists()]
        if missing_files:
            print(f"\n❌ Missing required files:")
            for file in missing_files:
                print(f"   - {file}")
            print(f"\nPlease run the setup scripts first:")
            print(f"   1. python scripts/00_setup_and_validate.py")
            print(f"   2. python scripts/01_prepare_codebook.py")
            print(f"   3. python scripts/02a_add_unique_ids.py")
            return False
        
        # Run pilots for each model
        results = {}
        total_time_start = datetime.now()
        
        for model in valid_models:
            model_start = datetime.now()
            success = run_pilot_for_model(model)
            model_end = datetime.now()
            
            results[model] = {
                "success": success,
                "duration": model_end - model_start
            }
        
        total_time_end = datetime.now()
        
        # Summary
        print(f"\n📊 MULTI-MODEL PILOT SUMMARY")
        print("=" * 60)
        
        successful_models = [m for m, r in results.items() if r["success"]]
        failed_models = [m for m, r in results.items() if not r["success"]]
        
        print(f"✅ Successful: {len(successful_models)}/{len(valid_models)}")
        print(f"❌ Failed: {len(failed_models)}/{len(valid_models)}")
        print(f"⏱️  Total time: {total_time_end - total_time_start}")
        
        if successful_models:
            print(f"\n🎉 Successful models:")
            for model in successful_models:
                duration = results[model]["duration"]
                print(f"   ✅ {model.split('/')[-1]} ({duration})")
        
        if failed_models:
            print(f"\n⚠️  Failed models:")
            for model in failed_models:
                print(f"   ❌ {model.split('/')[-1]}")
        
        print(f"\n💡 Next steps:")
        if successful_models:
            print("   1. python scripts/04a_analyze_results.py  # Compare model performance")
            print("   2. Check data/output/ for individual result files")
            print("   3. Use notebooks/analyze_pilot.ipynb for detailed analysis")
        else:
            print("   1. Check error messages above")
            print("   2. Verify API key and network connectivity")
            print("   3. Run individual pilots with --verbose for debugging")
        
        return len(successful_models) > 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Multi-model pilot interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during multi-model pilot: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
