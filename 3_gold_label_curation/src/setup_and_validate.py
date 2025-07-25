"""
ACSES Pilot Study - Quick Setup and Validation Script
This script helps validate your setup and run a quick test.
Automatically loads .env file if present.
"""

import os
import sys
import pandas as pd
import subprocess
from pathlib import Path

# --- Load .env file if present ---
try:
    from dotenv import load_dotenv
    dotenv_path = Path(__file__).parent.parent / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        print(f"✅ Loaded environment variables from {dotenv_path}")
    else:
        print(f"ℹ️  No .env file found at {dotenv_path}, skipping dotenv load.")
except ImportError:
    print("⚠️  python-dotenv not installed. .env file will not be loaded automatically.")
    print("   To enable .env support, install with: pip install python-dotenv")

def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a required file exists."""
    if os.path.exists(filepath):
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing - {filepath}")
        return False

def check_environment() -> bool:
    """Check if environment is properly configured."""
    print("🔍 CHECKING ENVIRONMENT SETUP")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version: {python_version.major}.{python_version.minor}.{python_version.micro} (requires 3.8+)")
        return False
    
    # Check required files
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    required_files = [
        (project_root / "data" / "input" / "kbli_codebook.csv", "KBLI Codebook"),
        (project_root / "data" / "input" / "mini_test.csv", "Mini Test Dataset"),
        (project_root / "prompts" / "master_prompt.txt", "Master Prompt Template"),
        (project_root / "requirements.txt", "Requirements File")
    ]
    
    all_files_exist = True
    for filepath, description in required_files:
        if not check_file_exists(str(filepath), description):
            all_files_exist = False
    
    # Check if enhanced dataset with UUIDs exists
    enhanced_dataset_path = project_root / "data" / "input" / "mini_test_with_ids.csv"
    enhanced_exists = check_file_exists(str(enhanced_dataset_path), "Enhanced Dataset with UUIDs (recommended)")
    
    if not enhanced_exists:
        print("💡 Consider running: python src/02a_add_unique_ids.py")
        print("   This adds UUID identifiers for better tracking and analysis.")
    
    # Check if hierarchical codebook exists (created by Phase 1)
    hierarchical_path = project_root / "data" / "output" / "kbli_codebook_hierarchical.csv"
    hierarchical_exists = check_file_exists(str(hierarchical_path), "Hierarchical Codebook (Phase 1 output)")
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY: Set (length: {len(api_key)})")
    else:
        print("❌ GEMINI_API_KEY: Not set")
        print("   Please set your API key:")
        print("   $env:GEMINI_API_KEY='your_key_here'  # PowerShell")
        return False
    
    return all_files_exist and bool(api_key), hierarchical_exists

def install_requirements() -> bool:
    """Install required packages."""
    print("\n📦 INSTALLING REQUIREMENTS")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Requirements installed successfully")
            return True
        else:
            print("❌ Failed to install requirements:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing requirements: {str(e)}")
        return False

def run_phase1() -> bool:
    """Run Phase 1: Codebook preparation."""
    print("\n🔄 RUNNING PHASE 1: CODEBOOK PREPARATION")
    print("=" * 50)
    
    try:
        script_path = Path(__file__).parent / "00_prepare_codebook.py"
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Phase 1 completed successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Phase 1 failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running Phase 1: {str(e)}")
        return False

def validate_data() -> bool:
    """Validate input data quality."""
    print("\n🔍 VALIDATING DATA QUALITY")
    print("=" * 50)
    
    try:
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        # Check mini_test.csv
        test_path = project_root / "data" / "input" / "mini_test.csv"
        test_df = pd.read_csv(test_path, dtype={'kbli_code': str})
        
        print(f"✅ Mini test dataset: {len(test_df)} samples")
        print(f"   Columns: {list(test_df.columns)}")
        print(f"   Unique KBLI codes: {test_df['kbli_code'].nunique()}")
        
        # Check for missing values
        missing_text = test_df['text'].isna().sum()
        missing_codes = test_df['kbli_code'].isna().sum()
        
        if missing_text > 0:
            print(f"⚠️  Warning: {missing_text} samples with missing text")
        if missing_codes > 0:
            print(f"⚠️  Warning: {missing_codes} samples with missing KBLI codes")
        
        # Check hierarchical codebook if it exists
        hierarchical_path = project_root / "data" / "output" / "kbli_codebook_hierarchical.csv"
        if hierarchical_path.exists():
            hier_df = pd.read_csv(hierarchical_path, dtype={'code_5': str})
            print(f"✅ Hierarchical codebook: {len(hier_df)} entries")
            
            # Check coverage
            test_codes = set(test_df['kbli_code'].unique())
            hier_codes = set(hier_df['code_5'].unique())
            coverage = len(test_codes.intersection(hier_codes))
            
            print(f"   Coverage: {coverage}/{len(test_codes)} test codes found in codebook")
            
            if coverage < len(test_codes):
                missing_codes = test_codes - hier_codes
                print(f"⚠️  Missing codes: {list(missing_codes)[:5]}{'...' if len(missing_codes) > 5 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating data: {str(e)}")
        return False

def run_quick_test() -> bool:
    """Run a quick test with a single sample."""
    print("\n🧪 RUNNING QUICK TEST")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        
        # Configure API
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        # Simple test
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content("Test: Respond with 'Hello, ACSES!'")
        
        if response.text and "Hello" in response.text:
            print("✅ API connection successful")
            print(f"   Response: {response.text.strip()}")
            return True
        else:
            print("❌ API test failed - unexpected response")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def main():
    """Main setup and validation function."""
    print("🚀 ACSES PILOT STUDY - SETUP & VALIDATION")
    print("=" * 60)
    print(f"Working directory: {os.getcwd()}")
    
    # Step 1: Check environment
    env_ok, hierarchical_exists = check_environment()
    if not env_ok:
        print("\n❌ Environment setup incomplete. Please fix the issues above.")
        return
    
    # Step 2: Install requirements
    # if not install_requirements():
    #     print("\n❌ Failed to install requirements. Please install manually.")
    #     return
    
    # Step 3: Run Phase 1 if needed
    if not hierarchical_exists:
        print("\n⚠️  Hierarchical codebook not found. Running Phase 1...")
        if not run_phase1():
            print("\n❌ Phase 1 failed. Cannot proceed.")
            return
    else:
        print("\n✅ Hierarchical codebook already exists. Skipping Phase 1.")
    
    # Step 4: Validate data
    if not validate_data():
        print("\n❌ Data validation failed. Please check your input files.")
        return
    
    # Step 5: Quick API test
    if not run_quick_test():
        print("\n❌ API test failed. Please check your API key and connection.")
        return
    
    # Success!
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("✅ Environment configured correctly")
    print("✅ Requirements installed")
    print("✅ Phase 1 (codebook preparation) ready")
    print("✅ Data validated")
    print("✅ API connection working")
    
    print("\n📋 NEXT STEPS:")
    print("1. Run single model pilot:")
    print("   python src/03a_run_pilot_study.py")
    print("\n2. Or run multi-model comparison:")
    print("   python src/03b_run_multi_model_pilot.py")
    print("\n3. Analyze results:")
    print("   jupyter notebook notebooks/analyze_pilot.ipynb")
    
    print(f"\n📚 For detailed instructions, see README.md")

if __name__ == "__main__":
    main()
