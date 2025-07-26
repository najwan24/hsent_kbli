"""
ACSES Pilot Study - Phase 2: Pilot Study Execution
This script runs the pilot study using Gemini API to evaluate KBLI code assignments.
Now with JSONL format and resume capability for robust execution.
"""

import pandas as pd
import json
import os
import time
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

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

# --- CONFIGURATION ---
MODEL_NAME = "models/gemini-2.5-flash-lite"  # The model you are testing
N_RUNS = 3  # Number of times to check each sample
TEMPERATURE = 0.7  # For creative reasoning
MAX_RETRIES = 3  # Maximum number of API call retries
RETRY_DELAY = 2  # Seconds to wait between retries

# Rate limiting configuration based on model
RPM_LIMITS = {
    "models/gemini-1.5-flash-latest": 15,  # 15 RPM for free tier
    "models/gemini-1.5-pro-latest": 2,    # 2 RPM for free tier
    "models/gemini-2.5-flash-lite": 15,   # 15 RPM for free tier
}

def get_rate_limit_delay(model_name: str) -> float:
    """
    Calculate the minimum delay between requests to respect rate limits.
    
    Args:
        model_name: The model being used
        
    Returns:
        Minimum delay in seconds between requests
    """
    rpm = RPM_LIMITS.get(model_name, 15)  # Default to 15 RPM
    # Add 10% buffer to be safe
    return (60.0 / rpm) * 1.1

def configure_gemini_api() -> None:
    """Configure the Gemini API client using environment variable."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not found. Please set it before running.")
    
    genai.configure(api_key=api_key)
    print("✅ Gemini API configured successfully")

def load_hierarchical_codebook(path: str) -> pd.DataFrame:
    """Load the hierarchical codebook CSV file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Hierarchical codebook not found at {path}")
    
    df = pd.read_csv(path, dtype={'code_5': str, 'code_4': str, 'code_3': str, 'code_2': str, 'code_1': str})
    print(f"✅ Loaded hierarchical codebook with {len(df)} entries")
    return df

def load_test_data(path: str) -> pd.DataFrame:
    """Load the mini test dataset with UUIDs (preferred) or fallback to original."""
    # Try to load enhanced dataset with UUIDs first
    enhanced_path = path.replace("mini_test.csv", "mini_test_with_ids.csv")
    
    if os.path.exists(enhanced_path):
        print(f"📂 Loading enhanced dataset with UUIDs: {os.path.basename(enhanced_path)}")
        df = pd.read_csv(enhanced_path, dtype={'kbli_code': str, 'sample_id': str})
        print(f"✅ Loaded {len(df)} samples with UUID identifiers")
        
        # Verify UUID column exists
        if 'sample_id' not in df.columns:
            print("⚠️  Warning: sample_id column not found in enhanced dataset")
            print("   Using row index as sample_id")
            df['sample_id'] = [f"row_{i}" for i in range(len(df))]
        else:
            print(f"✅ All samples have unique UUID identifiers")
            
        return df
        
    elif os.path.exists(path):
        print(f"📂 Loading original dataset (no UUIDs): {os.path.basename(path)}")
        df = pd.read_csv(path, dtype={'kbli_code': str})
        print(f"✅ Loaded {len(df)} samples")
        
        # Add temporary sample_id based on row index
        df['sample_id'] = [f"row_{i}" for i in range(len(df))]
        print("⚠️  Added temporary row-based IDs (consider running 02a_add_unique_ids.py)")
        
        return df
    else:
        raise FileNotFoundError(f"Test data not found at {path} or {enhanced_path}")

def load_master_template(path: str) -> str:
    """Load the master prompt template."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Master template not found at {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    print("✅ Loaded master prompt template")
    return template

def format_hierarchy(row: pd.Series) -> str:
    """
    Creates a clean, multi-line string for the prompt hierarchy.
    
    Args:
        row: A row from the hierarchical codebook DataFrame
        
    Returns:
        Formatted hierarchy string
    """
    hierarchy_lines = [
        f"- Section {row['code_1']}: {row['title_1']}",
        f"- Division {row['code_2']}: {row['title_2']}",
        f"- Group {row['code_3']}: {row['title_3']}",
        f"- Class {row['code_4']}: {row['title_4']}",
        f"- Sub-Class {row['code_5']}: {row['title_5']}"
    ]
    
    # Add description if available
    if pd.notna(row['desc_5']) and row['desc_5'].strip():
        hierarchy_lines.append(f"- Description: {row['desc_5']}")
    
    return "\n".join(hierarchy_lines)

def build_prompt_for_sample(template: str, sample: pd.Series, codebook: pd.DataFrame) -> Optional[str]:
    """
    Build the prompt for a specific sample.
    
    Args:
        template: The master prompt template
        sample: A row from the test dataset
        codebook: The hierarchical codebook DataFrame
        
    Returns:
        Formatted prompt string or None if code not found
    """
    # Get the specific code from the 'kbli_code' column
    code_to_check = str(sample['kbli_code'])
    
    # Find the row in our prepared hierarchical codebook
    rule_rows = codebook[codebook['code_5'] == code_to_check]
    
    if rule_rows.empty:
        return None
    
    rule_row = rule_rows.iloc[0]
    
    # Format the hierarchy into a clean string
    hierarchy_context = format_hierarchy(rule_row)
    
    # Inject all data into the prompt template
    final_prompt = template.replace("{job_description}", str(sample['text']))
    final_prompt = final_prompt.replace("{code_to_check}", code_to_check)
    final_prompt = final_prompt.replace("{hierarchy_context}", hierarchy_context)
    #print(f"Final prompt for {code_to_check}:\n{final_prompt}")
    return final_prompt

def extract_json_from_response(text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from the API response.
    
    Args:
        text: Raw response text from the API
        
    Returns:
        Parsed JSON dictionary
    """
    # Try to find JSON block marked with ```json
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find any JSON object in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            raise ValueError(f"No JSON found in response: {text[:200]}...")
    
    # Parse the JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}\nJSON string: {json_str[:200]}...")

def call_gemini_api(prompt: str, model_name: str, temperature: float) -> str:
    """
    Call the Gemini API with retry logic.
    
    Args:
        prompt: The formatted prompt
        model_name: Name of the model to use
        temperature: Temperature parameter for generation
        
    Returns:
        Raw response text from the API
    """
    model = genai.GenerativeModel(model_name)
    
    generation_config = genai.types.GenerationConfig(
        temperature=temperature,
        top_p=0.8,
        top_k=40,
        max_output_tokens=2048,
    )
    
    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response.text:
                return response.text
            else:
                raise ValueError("Empty response from API")
                
        except Exception as e:
            error_str = str(e)
            print(f"API call attempt {attempt + 1} failed: {error_str[:100]}...")
            
            # Check if it's a rate limiting error
            if "ResourceExhausted" in error_str or "429" in error_str:
                # Extract retry delay from error message if available
                retry_delay_match = re.search(r'retry_delay.*?seconds: (\d+)', error_str)
                if retry_delay_match:
                    suggested_delay = int(retry_delay_match.group(1))
                    print(f"  Rate limit hit, waiting {suggested_delay}s as suggested...")
                    time.sleep(suggested_delay)
                else:
                    # Use our calculated rate limit delay
                    rate_delay = get_rate_limit_delay(MODEL_NAME)
                    print(f"  Rate limit hit, waiting {rate_delay:.1f}s...")
                    time.sleep(rate_delay)
            elif attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
            else:
                raise

def add_metadata_to_result(result: Dict[str, Any], sample: pd.Series, run_number: int, 
                          model_name: str, processing_time: float) -> Dict[str, Any]:
    """
    Add metadata to the parsed result for later analysis.
    
    Args:
        result: Parsed JSON result from the API
        sample: The original sample data
        run_number: Which run this is (1 to N_RUNS)
        model_name: Name of the model used
        processing_time: Time taken for this API call
        
    Returns:
        Result dictionary with added metadata
    """
    # Use UUID sample_id if available, otherwise fall back to row index
    sample_id = sample.get('sample_id', f"row_{getattr(sample, 'name', 0)}")
    
    metadata = {
        'sample_id': str(sample_id),  # Ensure it's a string
        'original_row_index': getattr(sample, 'name', 0),  # Preserve original row info
        'original_text': str(sample['text']),
        'assigned_kbli_code': str(sample['kbli_code']),
        'category': str(sample.get('category', 'N/A')),
        'run_number': run_number,
        'model_name': model_name,
        'timestamp': datetime.now().isoformat(),
        'processing_time_seconds': processing_time,
        'success': True
    }
    
    # Add UUID creation timestamp if available
    if 'id_created_at' in sample:
        metadata['sample_id_created_at'] = str(sample['id_created_at'])
    
    # Merge with the LLM result
    full_result = {**metadata, **result}
    return full_result

def create_error_record(sample: pd.Series, error: Exception, run_number: int, 
                       model_name: str) -> Dict[str, Any]:
    """
    Create an error record when API call fails.
    
    Args:
        sample: The original sample data
        error: The exception that occurred
        run_number: Which run this is
        model_name: Name of the model used
        
    Returns:
        Error record dictionary
    """
    # Use UUID sample_id if available, otherwise fall back to row index
    sample_id = sample.get('sample_id', f"row_{getattr(sample, 'name', 0)}")
    
    error_record = {
        'sample_id': str(sample_id),
        'original_row_index': getattr(sample, 'name', 0),
        'original_text': str(sample['text']),
        'assigned_kbli_code': str(sample['kbli_code']),
        'category': str(sample.get('category', 'N/A')),
        'run_number': run_number,
        'model_name': model_name,
        'timestamp': datetime.now().isoformat(),
        'success': False,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'is_correct': None,
        'confidence_score': None,
        'reasoning': None,
        'alternative_codes': [],
        'alternative_reasoning': None
    }
    
    # Add UUID creation timestamp if available
    if 'id_created_at' in sample:
        error_record['sample_id_created_at'] = str(sample['id_created_at'])
    
    return error_record

def load_existing_results(output_path: str) -> tuple[list, set]:
    """
    Load existing results from JSONL file to enable resumption.
    
    Returns:
        tuple: (list of existing results, set of completed sample_run combinations)
    """
    existing_results = []
    completed_runs = set()
    
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            result = json.loads(line)
                            existing_results.append(result)
                            # Create unique key for sample_id + run_number
                            sample_id = result.get('sample_id', -1)
                            run_num = result.get('run_number', -1)
                            # Only mark as completed if it was successful
                            if result.get('success', False):
                                completed_runs.add((sample_id, run_num))
                        except json.JSONDecodeError as e:
                            print(f"⚠️  Warning: Invalid JSON on line {line_num}: {e}")
                            continue
            
            print(f"📂 Found {len(existing_results)} existing results")
            
            # Count successful vs failed results
            successful_runs = sum(1 for r in existing_results if r.get('success', False))
            failed_runs = len(existing_results) - successful_runs
            
            print(f"📊 Completed runs: {len(completed_runs)} successful, {failed_runs} failed")
            print(f"🔄 Failed runs will be retried on resume")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load existing results: {e}")
            return [], set()
    
    return existing_results, completed_runs

def save_result_to_jsonl(result: Dict[str, Any], output_path: str) -> bool:
    """
    Append a single result to JSONL file immediately.
    
    Args:
        result: Result dictionary to save
        output_path: Path to JSONL file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'a', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
            f.write('\n')
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not save result: {e}")
        return False

def main():
    """Main function to run the pilot study."""
    print("🚀 Starting ACSES Pilot Study")
    print(f"Model: {MODEL_NAME}")
    print(f"Runs per sample: {N_RUNS}")
    print(f"Temperature: {TEMPERATURE}")
    
    # Show rate limiting info
    rpm_limit = RPM_LIMITS.get(MODEL_NAME, 15)
    rate_delay = get_rate_limit_delay(MODEL_NAME)
    print(f"Rate limit: {rpm_limit} requests per minute")
    print(f"Delay between requests: {rate_delay:.1f} seconds")
    print(f"Estimated time per sample: {rate_delay * N_RUNS:.1f} seconds")
    
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    codebook_path = os.path.join(project_root, "data", "output", "kbli_codebook_hierarchical.csv")
    test_data_path = os.path.join(project_root, "data", "input", "mini_test.csv")
    template_path = os.path.join(project_root, "prompts", "master_prompt.txt")
    
    # Create output filename with model name - use .jsonl extension
    output_filename = f"pilot_results_{MODEL_NAME.replace('-', '_')}.jsonl"
    output_path = os.path.join(project_root, "data", "output", output_filename)
    
    try:
        # 1. LOAD RESOURCES
        print("\n📂 Loading resources...")
        configure_gemini_api()
        codebook = load_hierarchical_codebook(codebook_path)
        test_data = load_test_data(test_data_path)
        master_template = load_master_template(template_path)
        
        # 2. LOAD EXISTING RESULTS FOR RESUMPTION
        print("\n🔄 Checking for existing results...")
        existing_results, completed_runs = load_existing_results(output_path)
        
        total_samples = len(test_data)
        total_expected_runs = total_samples * N_RUNS
        
        print(f"\n� Progress Summary:")
        print(f"Total samples: {total_samples}")
        print(f"Expected total runs: {total_expected_runs}")
        print(f"Already completed runs: {len(completed_runs)}")
        print(f"Remaining runs: {total_expected_runs - len(completed_runs)}")
        
        if len(completed_runs) == total_expected_runs:
            print("🎉 All runs already completed! Nothing to do.")
            return
        
        processed_samples = 0
        new_results_count = 0
        
        print(f"\n🔄 Processing samples (resuming from existing results)...")
        
        # 3. ITERATE AND PROCESS
        for idx, (_, sample) in enumerate(test_data.iterrows()):
            # Use UUID sample_id if available, otherwise use row index
            sample_id = sample.get('sample_id', f"row_{idx}")
            
            print(f"\nProcessing sample {idx + 1}/{total_samples}: {sample['kbli_code']} (ID: {sample_id})")
            
            # Build the prompt once per sample
            prompt = build_prompt_for_sample(master_template, sample, codebook)
            
            if prompt is None:
                print(f"⚠️  Warning: Code {sample['kbli_code']} not in codebook. Skipping.")
                continue
            
            # Check which runs are already completed for this sample
            sample_completed_runs = {run_num for (sid, run_num) in completed_runs if sid == sample_id}
            remaining_runs = [run_num for run_num in range(1, N_RUNS + 1) if run_num not in sample_completed_runs]
            
            if not remaining_runs:
                print(f"  ✅ All runs already completed for this sample")
                processed_samples += 1
                continue
            
            print(f"  📋 Need to complete runs: {remaining_runs}")
            
            # Run the remaining runs for this sample
            for run_num in remaining_runs:
                start_time = time.time()
                
                try:
                    print(f"  Run {run_num}/{N_RUNS}...", end=" ")
                    
                    # Call the API
                    raw_response = call_gemini_api(prompt, MODEL_NAME, TEMPERATURE)
                    
                    # Parse the response
                    parsed_json = extract_json_from_response(raw_response)
                    
                    processing_time = time.time() - start_time
                    
                    # Add our own metadata for later analysis
                    full_result = add_metadata_to_result(
                        parsed_json, sample, run_num, MODEL_NAME, processing_time
                    )
                    
                    # Save result immediately to JSONL file
                    if save_result_to_jsonl(full_result, output_path):
                        completed_runs.add((sample_id, run_num))
                        new_results_count += 1
                        print(f"✅ ({processing_time:.1f}s) [Saved]")
                    else:
                        print(f"⚠️  ({processing_time:.1f}s) [Save failed]")
                    
                except Exception as e:
                    processing_time = time.time() - start_time
                    error_type = type(e).__name__
                    
                    # Special handling for ResourceExhausted errors
                    if "ResourceExhausted" in str(e) or "429" in str(e) or "quota" in str(e).lower():
                        print(f"⚠️  Quota exceeded: {str(e)[:80]}...")
                        print(f"  💡 This run will be retried when you resume the script")
                    else:
                        print(f"❌ Error ({error_type}): {str(e)[:50]}...")
                    
                    # Log the error so we know which ones failed
                    error_record = create_error_record(sample, e, run_num, MODEL_NAME)
                    
                    # Save error record immediately
                    if save_result_to_jsonl(error_record, output_path):
                        # Don't mark error runs as completed - let them retry on resume
                        new_results_count += 1
                        print(f"  📝 Error logged and saved (will retry on resume)")
                
                # Rate-limited delay based on model
                rate_delay = get_rate_limit_delay(MODEL_NAME)
                print(f"  ⏳ Waiting {rate_delay:.1f}s (rate limit: {RPM_LIMITS.get(MODEL_NAME, 15)} RPM)")
                time.sleep(rate_delay)
            
            processed_samples += 1
            
            # Progress update every 10 samples
            if processed_samples % 10 == 0:
                total_completed = len(existing_results) + new_results_count
                print(f"📊 Progress: {processed_samples}/{total_samples} samples, {total_completed} total results")
        
        # 4. FINAL SUMMARY
        total_completed = len(existing_results) + new_results_count
        final_success_rate = 0
        
        # Calculate success rate from all results
        if output_path and os.path.exists(output_path):
            successful_count = 0
            total_count = 0
            
            with open(output_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            result = json.loads(line)
                            total_count += 1
                            if result.get('success', False):
                                successful_count += 1
                        except:
                            continue
            
            final_success_rate = successful_count / total_count if total_count > 0 else 0
        
        print(f"\n🎉 Pilot study complete!")
        print(f"Total samples processed: {processed_samples}")
        print(f"New results generated: {new_results_count}")
        print(f"Total results in file: {total_completed}")
        print(f"Success rate: {final_success_rate:.1%}")
        print(f"Results saved to: {output_path}")
        print(f"\n💡 Note: Results are saved in JSONL format (one JSON per line)")
        print(f"💡 To resume if interrupted, just run this script again!")
        
    except KeyboardInterrupt:
        print(f"\n\n⏸️  Process interrupted by user")
        print(f"📂 Partial results saved to: {output_path}")
        print(f"🔄 To resume, run this script again - it will continue from where it left off")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        print(f"📂 Partial results (if any) saved to: {output_path}")
        print(f"🔄 To resume, run this script again after fixing the error")
        raise

if __name__ == "__main__":
    main()
