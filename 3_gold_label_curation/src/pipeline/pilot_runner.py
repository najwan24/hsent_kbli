"""
Consolidated Pilot Study Runner
Main execution logic for running pilot studies with different models and datasets.
"""

import os
import time
import pandas as pd
from typing import Dict, Any, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path

from ..api.gemini_client import GeminiClient
from ..data.data_loader import DataLoader
from ..utils.json_parser import (
    extract_json_from_response, 
    save_result_to_jsonl, 
    load_existing_results,
    calculate_success_rate
)


class PilotRunner:
    """Main class for running pilot studies."""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the pilot runner.
        
        Args:
            project_root: Path to project root (if None, auto-detects)
        """
        if project_root is None:
            current_file = Path(__file__)
            self.project_root = current_file.parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.data_loader = DataLoader(str(self.project_root))
        self.gemini_client = None
    
    def initialize_api(self, api_key: Optional[str] = None) -> None:
        """Initialize the Gemini API client."""
        self.gemini_client = GeminiClient(api_key=api_key)
    
    def format_hierarchy(self, row: pd.Series) -> str:
        """
        Create a clean, multi-line string for the prompt hierarchy.
        
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
    
    def build_prompt_for_sample(self, template: str, sample: pd.Series, 
                               codebook: pd.DataFrame) -> Optional[str]:
        """
        Build the prompt for a specific sample.
        
        Args:
            template: The master prompt template
            sample: A row from the test dataset
            codebook: The hierarchical codebook DataFrame
            
        Returns:
            Formatted prompt string or None if code not found
        """
        code_to_check = str(sample['kbli_code'])
        
        # Find the row in our prepared hierarchical codebook
        rule_rows = codebook[codebook['code_5'] == code_to_check]
        
        if rule_rows.empty:
            return None
        
        rule_row = rule_rows.iloc[0]
        hierarchy_context = self.format_hierarchy(rule_row)
        
        # Inject all data into the prompt template
        final_prompt = template.replace("{job_description}", str(sample['text']))
        final_prompt = final_prompt.replace("{code_to_check}", code_to_check)
        final_prompt = final_prompt.replace("{hierarchy_context}", hierarchy_context)
        
        return final_prompt
    
    def add_metadata_to_result(self, result: Dict[str, Any], sample: pd.Series, 
                              run_number: int, model_name: str, 
                              processing_time: float) -> Dict[str, Any]:
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
        sample_id = sample.get('sample_id', f"row_{getattr(sample, 'name', 0)}")
        
        metadata = {
            'sample_id': str(sample_id),
            'original_row_index': getattr(sample, 'name', 0),
            'original_text': str(sample['text']),
            'assigned_kbli_code': str(sample['kbli_code']),
            'category': str(sample.get('category', 'N/A')),
            'run_number': run_number,
            'model_name': model_name,
            'dataset_name': sample.get('dataset_name', 'unknown.csv'),
            'timestamp': datetime.now().isoformat(),
            'processing_time_seconds': processing_time,
            'success': True
        }
        
        # Add UUID creation timestamp if available
        if 'id_created_at' in sample:
            metadata['sample_id_created_at'] = str(sample['id_created_at'])
        
        return {**metadata, **result}
    
    def create_error_record(self, sample: pd.Series, error: Exception, 
                           run_number: int, model_name: str) -> Dict[str, Any]:
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
        sample_id = sample.get('sample_id', f"row_{getattr(sample, 'name', 0)}")
        
        error_record = {
            'sample_id': str(sample_id),
            'original_row_index': getattr(sample, 'name', 0),
            'original_text': str(sample['text']),
            'assigned_kbli_code': str(sample['kbli_code']),
            'category': str(sample.get('category', 'N/A')),
            'run_number': run_number,
            'model_name': model_name,
            'dataset_name': sample.get('dataset_name', 'unknown.csv'),
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
    
    def run_pilot_study(self, model_name: str, dataset_filename: str, 
                       n_runs: int = 3, temperature: float = 0.7,
                       output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the complete pilot study.
        
        Args:
            model_name: Name of the Gemini model to use
            dataset_filename: Name of the dataset file
            n_runs: Number of runs per sample
            temperature: Temperature for generation
            output_dir: Custom output directory
            
        Returns:
            Dictionary with execution statistics
        """
        if self.gemini_client is None:
            self.initialize_api()
        
        print("🚀 Starting ACSES Pilot Study")
        print(f"Model: {model_name}")
        print(f"Dataset: {dataset_filename}")
        print(f"Runs per sample: {n_runs}")
        print(f"Temperature: {temperature}")
        
        # Show rate limiting info
        available_models = self.gemini_client.get_available_models()
        rpm_limit = available_models.get(model_name, {}).get("rpm", 15)
        rate_delay = self.gemini_client.get_rate_limit_delay(model_name)
        
        print(f"Rate limit: {rpm_limit} requests per minute")
        print(f"Delay between requests: {rate_delay:.1f} seconds")
        print(f"Estimated time per sample: {rate_delay * n_runs:.1f} seconds")
        
        # Define paths
        codebook_path = self.project_root / "data" / "output" / "kbli_codebook_hierarchical.csv"
        template_path = self.project_root / "prompts" / "master_prompt.txt"
        
        # Create output filename
        model_safe_name = model_name.replace('/', '_').replace('-', '_')
        dataset_safe_name = os.path.splitext(dataset_filename)[0]
        output_filename = f"{model_safe_name}_{dataset_safe_name}.jsonl"
        
        if output_dir:
            output_path = Path(output_dir) / output_filename
        else:
            # Save to pilot_results_models subdirectory for better organization
            pilot_results_dir = self.project_root / "data" / "output" / "pilot_results_models"
            pilot_results_dir.mkdir(exist_ok=True)  # Ensure directory exists
            output_path = pilot_results_dir / output_filename
        
        try:
            # 1. LOAD RESOURCES
            print("\n📂 Loading resources...")
            codebook = self.data_loader.load_hierarchical_codebook(str(codebook_path))
            test_data = self.data_loader.load_test_data(dataset_filename)
            test_data['dataset_name'] = dataset_filename
            master_template = self.data_loader.load_master_template(str(template_path))
            
            # 2. LOAD EXISTING RESULTS FOR RESUMPTION
            print("\n🔄 Checking for existing results...")
            existing_results, completed_runs = load_existing_results(str(output_path))
            
            total_samples = len(test_data)
            total_expected_runs = total_samples * n_runs
            
            print(f"\n📊 Progress Summary:")
            print(f"Total samples: {total_samples}")
            print(f"Expected total runs: {total_expected_runs}")
            print(f"Already completed runs: {len(completed_runs)}")
            print(f"Remaining runs: {total_expected_runs - len(completed_runs)}")
            
            if len(completed_runs) == total_expected_runs:
                print("🎉 All runs already completed! Nothing to do.")
                return self._create_execution_stats(
                    total_samples, len(existing_results), 0, 
                    calculate_success_rate(str(output_path)), str(output_path)
                )
            
            processed_samples = 0
            new_results_count = 0
            
            print(f"\n🔄 Processing samples (resuming from existing results)...")
            
            # 3. ITERATE AND PROCESS
            resource_exhausted = False
            for idx, (_, sample) in enumerate(test_data.iterrows()):
                sample_id = sample.get('sample_id', f"row_{idx}")
                
                print(f"\nProcessing sample {idx + 1}/{total_samples}: {sample['kbli_code']} (ID: {sample_id})")
                
                prompt = self.build_prompt_for_sample(master_template, sample, codebook)
                
                if prompt is None:
                    print(f"⚠️  Warning: Code {sample['kbli_code']} not in codebook. Skipping.")
                    continue
                
                # Check completed runs for this sample
                sample_completed_runs = {run_num for (sid, run_num) in completed_runs if sid == sample_id}
                remaining_runs = [run_num for run_num in range(1, n_runs + 1) if run_num not in sample_completed_runs]
                
                if not remaining_runs:
                    print(f"  ✅ All runs already completed for this sample")
                    processed_samples += 1
                    continue
                
                print(f"  📋 Need to complete runs: {remaining_runs}")
                
                # Run the remaining runs for this sample
                for run_num in remaining_runs:
                    if resource_exhausted:
                        print("⏹️  Stopping further processing due to ResourceExhausted error.")
                        break
                    
                    start_time = time.time()
                    try:
                        print(f"  Run {run_num}/{n_runs}...", end=" ")
                        
                        raw_response = self.gemini_client.generate_content(
                            prompt, model_name, temperature
                        )
                        parsed_json = extract_json_from_response(raw_response)
                        processing_time = time.time() - start_time
                        
                        full_result = self.add_metadata_to_result(
                            parsed_json, sample, run_num, model_name, processing_time
                        )
                        
                        if save_result_to_jsonl(full_result, str(output_path)):
                            completed_runs.add((sample_id, run_num))
                            new_results_count += 1
                            print(f"✅ ({processing_time:.1f}s) [Saved]")
                        else:
                            print(f"⚠️  ({processing_time:.1f}s) [Save failed]")
                            
                    except Exception as e:
                        processing_time = time.time() - start_time
                        error_type = type(e).__name__
                        
                        if "ResourceExhausted" in str(e) or "429" in str(e) or "quota" in str(e).lower():
                            print(f"⚠️  Quota exceeded: {str(e)[:80]}...")
                            print(f"⏹️  Breaking loop due to ResourceExhausted error. No output will be appended for this sample.")
                            resource_exhausted = True
                            break
                        else:
                            print(f"❌ Error ({error_type}): {str(e)[:50]}...")
                            error_record = self.create_error_record(sample, e, run_num, model_name)
                            
                            if save_result_to_jsonl(error_record, str(output_path)):
                                new_results_count += 1
                                print(f"  📝 Error logged and saved (will retry on resume)")
                    
                    # Rate-limited delay
                    print(f"  ⏳ Waiting {rate_delay:.1f}s (rate limit: {rpm_limit} RPM)")
                    time.sleep(rate_delay)
                
                processed_samples += 1
                
                if processed_samples % 10 == 0:
                    total_completed = len(existing_results) + new_results_count
                    print(f"📊 Progress: {processed_samples}/{total_samples} samples, {total_completed} total results")
                
                if resource_exhausted:
                    break
            
            # 4. FINAL SUMMARY
            final_success_rate = calculate_success_rate(str(output_path))
            total_completed = len(existing_results) + new_results_count
            
            print(f"\n🎉 Pilot study complete!")
            print(f"Total samples processed: {processed_samples}")
            print(f"New results generated: {new_results_count}")
            print(f"Total results in file: {total_completed}")
            print(f"Success rate: {final_success_rate:.1%}")
            print(f"Results saved to: {output_path}")
            print(f"\n💡 Note: Results are saved in JSONL format (one JSON per line)")
            print(f"💡 To resume if interrupted, just run this script again!")
            
            return self._create_execution_stats(
                processed_samples, total_completed, new_results_count,
                final_success_rate, str(output_path)
            )
            
        except KeyboardInterrupt:
            print(f"\n\n⏸️  Process interrupted by user")
            print(f"📂 Partial results saved to: {output_path}")
            print(f"🔄 To resume, run this script again - it will continue from where it left off")
            raise
            
        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")
            print(f"📂 Partial results (if any) saved to: {output_path}")
            print(f"🔄 To resume, run this script again after fixing the error")
            raise
    
    def _create_execution_stats(self, processed_samples: int, total_completed: int,
                               new_results: int, success_rate: float, 
                               output_path: str) -> Dict[str, Any]:
        """Create execution statistics dictionary."""
        return {
            'processed_samples': processed_samples,
            'total_completed': total_completed,
            'new_results_generated': new_results,
            'success_rate': success_rate,
            'output_path': output_path,
            'completed_at': datetime.now().isoformat()
        }
