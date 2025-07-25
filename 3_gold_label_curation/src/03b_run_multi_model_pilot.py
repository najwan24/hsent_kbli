"""
ACSES Pilot Study - Model Comparison Script
This script runs the pilot study for multiple models to compare their performance.
Updated to work with the new JSONL format and resume capability.
"""

import os
import sys
import subprocess
import time
from datetime import datetime

# --- Load .env file if present ---
try:
    from dotenv import load_dotenv
    from pathlib import Path
    dotenv_path = Path(__file__).parent.parent / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        print(f"✅ Loaded environment variables from {dotenv_path}")
except ImportError:
    print("⚠️  python-dotenv not installed. .env file will not be loaded automatically.")

# Models to test
MODELS_TO_TEST = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest"
]

def run_pilot_for_model(model_name: str) -> bool:
    """
    Run the pilot study for a specific model.
    
    Args:
        model_name: Name of the model to test
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n🚀 Starting pilot study for {model_name}")
    print("=" * 60)
    
    # Set environment variable for the current model
    env = os.environ.copy()
    
    # Modify the pilot script to use the specified model
    script_path = os.path.join(os.path.dirname(__file__), "03a_run_pilot_study.py")
    
    # Read the original script
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    # Replace the MODEL_NAME configuration
    original_model_line = 'MODEL_NAME = "gemini-1.5-flash-latest"'
    new_model_line = f'MODEL_NAME = "{model_name}"'
    
    if original_model_line in script_content:
        modified_content = script_content.replace(original_model_line, new_model_line)
    else:
        # Try to find any MODEL_NAME assignment
        import re
        pattern = r'MODEL_NAME\s*=\s*["\'][^"\']*["\']'
        modified_content = re.sub(pattern, new_model_line, script_content)
    
    # Create a temporary script file
    temp_script = f"temp_pilot_{model_name.replace('-', '_').replace('.', '_')}.py"
    temp_script_path = os.path.join(os.path.dirname(__file__), temp_script)
    
    try:
        # Write the modified script
        with open(temp_script_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        # Run the modified script
        start_time = time.time()
        result = subprocess.run([sys.executable, temp_script_path], 
                              capture_output=True, text=True, env=env)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ Pilot study for {model_name} completed successfully!")
            print(f"⏱️  Duration: {duration/60:.1f} minutes")
            print("📝 Output:")
            print(result.stdout)
            return True
        else:
            print(f"❌ Pilot study for {model_name} failed!")
            print("📝 Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running pilot for {model_name}: {str(e)}")
        return False
        
    finally:
        # Clean up temporary script
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)

def main():
    """Run pilot studies for all specified models."""
    print("🔬 ACSES Pilot Study - Multi-Model Comparison")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Models to test: {', '.join(MODELS_TO_TEST)}")
    
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("\n❌ ERROR: GEMINI_API_KEY environment variable not set!")
        print("Please set your Gemini API key before running this script.")
        print("You can:")
        print("1. Create a .env file with GEMINI_API_KEY=your_key")
        print("2. Set the environment variable directly")
        return
    
    # Check if prerequisites are ready
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    required_files = [
        os.path.join(project_root, "data", "output", "kbli_codebook_hierarchical.csv"),
        os.path.join(project_root, "data", "input", "mini_test.csv"),
        os.path.join(project_root, "prompts", "master_prompt.txt")
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("\n❌ ERROR: Missing required files:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nPlease run the codebook preparation script first:")
        print("python src/00_prepare_codebook.py")
        return
    
    # Run pilots for each model
    results = {}
    total_start_time = time.time()
    
    for model in MODELS_TO_TEST:
        success = run_pilot_for_model(model)
        results[model] = success
        
        if success:
            print(f"\n✅ {model}: SUCCESS")
        else:
            print(f"\n❌ {model}: FAILED")
        
        # Add delay between models to be respectful to the API
        if model != MODELS_TO_TEST[-1]:  # Don't wait after the last model
            print("\n⏸️  Waiting 30 seconds before next model...")
            time.sleep(30)
    
    # Summary
    total_duration = time.time() - total_start_time
    
    print("\n" + "=" * 60)
    print("📊 MULTI-MODEL PILOT STUDY COMPLETE")
    print("=" * 60)
    print(f"⏱️  Total duration: {total_duration/60:.1f} minutes")
    print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📋 Results Summary:")
    successful_models = []
    failed_models = []
    
    for model, success in results.items():
        if success:
            print(f"  ✅ {model}: SUCCESS")
            successful_models.append(model)
        else:
            print(f"  ❌ {model}: FAILED")
            failed_models.append(model)
    
    print(f"\n📈 Success rate: {len(successful_models)}/{len(MODELS_TO_TEST)} models")
    
    if successful_models:
        print(f"\n🎉 Successfully completed pilots for: {', '.join(successful_models)}")
        print("\n📊 Next steps:")
        print("1. Open notebooks/analyze_pilot.ipynb")
        print("2. Load and compare results from all models")
        print("3. Make data-driven model selection decision")
    
    if failed_models:
        print(f"\n⚠️  Failed pilots for: {', '.join(failed_models)}")
        print("Please check the error messages above and retry if needed.")

if __name__ == "__main__":
    main()
