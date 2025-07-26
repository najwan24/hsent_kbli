"""
Analysis module for ACSES pilot study results.
Provides comprehensive analysis of JSONL result files.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import pandas as pd


class ResultsAnalyzer:
    """Analyzes pilot study results from JSONL files."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the analyzer.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "output"
        
    def load_results(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Load results from JSONL file for a specific model.
        
        Args:
            model_name: Name of the model (e.g., 'gemini_2.5_flash_lite')
            
        Returns:
            List of result dictionaries
        """
        # Try different possible file locations
        possible_paths = [
            # New naming convention (models_MODEL_DATASET.jsonl) - try original name first
            self.output_dir / "pilot_results_models" / f"models_{model_name}_mini_test_with_ids.jsonl",
            self.output_dir / "pilot_results_models" / f"models_{model_name}_mini_test.jsonl",
            # New naming convention with character replacement
            self.output_dir / "pilot_results_models" / f"models_{model_name.replace('-', '_').replace('.', '_')}_mini_test_with_ids.jsonl",
            self.output_dir / "pilot_results_models" / f"models_{model_name.replace('-', '_').replace('.', '_')}_mini_test.jsonl",
            # Legacy naming conventions
            self.output_dir / f"pilot_results_{model_name}.jsonl",
            self.output_dir / "pilot_results_models" / f"{model_name}.jsonl",
            self.output_dir / f"pilot_results_{model_name.replace('-', '_').replace('.', '_')}.jsonl"
        ]
        
        for file_path in possible_paths:
            if file_path.exists():
                return self._load_jsonl_file(file_path)
        
        raise FileNotFoundError(f"Results file not found for model: {model_name}")
    
    def _load_jsonl_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load and parse JSONL file."""
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            results.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            print(f"⚠️  Warning: Skipping malformed JSON at line {line_num}: {e}")
                            continue
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return []
            
        return results
    
    def analyze_model_results(self, model_name: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of results for a specific model.
        
        Args:
            model_name: Name of the model to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            results = self.load_results(model_name)
        except FileNotFoundError as e:
            return {"error": str(e), "model": model_name}
        
        if not results:
            return {"error": "No results found", "model": model_name}
        
        # Basic statistics
        total_entries = len(results)
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        # Sample and run coverage
        samples = set(r.get('sample_id', 'unknown') for r in results)
        sample_runs = defaultdict(set)
        successful_sample_runs = defaultdict(set)
        
        for result in results:
            sample_id = result.get('sample_id', 'unknown')
            run_num = result.get('run_number', 0)
            sample_runs[sample_id].add(run_num)
            
            if result.get('success', False):
                successful_sample_runs[sample_id].add(run_num)
        
        # Completeness analysis
        expected_runs = {1, 2, 3}
        complete_samples = []
        incomplete_samples = []
        
        for sample_id in samples:
            successful_runs = successful_sample_runs.get(sample_id, set())
            if successful_runs == expected_runs:
                complete_samples.append(sample_id)
            else:
                missing_runs = expected_runs - successful_runs
                incomplete_samples.append((sample_id, missing_runs))
        
        # Error analysis
        error_analysis = {}
        if failed:
            error_types = defaultdict(int)
            for result in failed:
                error_type = result.get('error_type', 'Unknown')
                error_types[error_type] += 1
            error_analysis = dict(error_types)
        
        return {
            "model": model_name,
            "total_entries": total_entries,
            "successful_calls": len(successful),
            "failed_calls": len(failed),
            "success_rate": len(successful) / total_entries if total_entries > 0 else 0,
            "unique_samples": len(samples),
            "complete_samples": len(complete_samples),
            "incomplete_samples": len(incomplete_samples),
            "incomplete_details": incomplete_samples[:10],  # First 10 for brevity
            "error_analysis": error_analysis,
            "sample_coverage": len(sample_runs)
        }
    
    def print_analysis_report(self, analysis: Dict[str, Any]) -> None:
        """Print a formatted analysis report."""
        if "error" in analysis:
            print(f"❌ Error analyzing {analysis.get('model', 'unknown')}: {analysis['error']}")
            return
        
        print(f"📊 ANALYSIS REPORT: {analysis['model'].upper()}")
        print("=" * 60)
        
        # Basic statistics
        print(f"📋 Total entries: {analysis['total_entries']}")
        print(f"✅ Successful calls: {analysis['successful_calls']}")
        print(f"❌ Failed calls: {analysis['failed_calls']}")
        print(f"📈 Success rate: {analysis['success_rate']:.1%}")
        
        # Sample coverage
        print(f"\n🆔 Unique samples processed: {analysis['unique_samples']}")
        print(f"✅ Complete samples: {analysis['complete_samples']}")
        print(f"⚠️  Incomplete samples: {analysis['incomplete_samples']}")
        
        # Error breakdown
        if analysis.get('error_analysis'):
            print(f"\n❌ ERROR BREAKDOWN:")
            for error_type, count in analysis['error_analysis'].items():
                print(f"• {error_type}: {count}")
        
        # Incomplete samples details
        if analysis.get('incomplete_details'):
            print(f"\n🔄 SAMPLES NEEDING RETRY:")
            for sample_id, missing_runs in analysis['incomplete_details']:
                display_id = sample_id[:8] + "..." if len(str(sample_id)) > 8 else sample_id
                print(f"• {display_id} missing runs: {sorted(missing_runs)}")
            
            remaining = analysis['incomplete_samples'] - len(analysis['incomplete_details'])
            if remaining > 0:
                print(f"• ... and {remaining} more")
    
    def compare_models(self, model_names: List[str]) -> Dict[str, Any]:
        """
        Compare analysis results across multiple models.
        
        Args:
            model_names: List of model names to compare
            
        Returns:
            Comparison results dictionary
        """
        comparisons = {}
        
        for model in model_names:
            comparisons[model] = self.analyze_model_results(model)
        
        return {
            "models": comparisons,
            "summary": self._generate_comparison_summary(comparisons)
        }
    
    def _generate_comparison_summary(self, comparisons: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for model comparison."""
        valid_results = {k: v for k, v in comparisons.items() if "error" not in v}
        
        if not valid_results:
            return {"error": "No valid results to compare"}
        
        # Find best performing model
        best_model = max(valid_results.keys(), 
                        key=lambda k: valid_results[k]['success_rate'])
        
        return {
            "best_model": best_model,
            "best_success_rate": valid_results[best_model]['success_rate'],
            "models_compared": len(valid_results),
            "total_samples_processed": sum(r['unique_samples'] for r in valid_results.values())
        }


def analyze_gemini_2_5_results(project_root: Optional[Path] = None) -> None:
    """
    Convenience function to analyze Gemini 2.5 Flash Lite results.
    This maintains compatibility with existing usage.
    """
    analyzer = ResultsAnalyzer(project_root)
    analysis = analyzer.analyze_model_results("gemini_2.5_flash_lite")
    analyzer.print_analysis_report(analysis)
    
    # Additional guidance
    if analysis.get('incomplete_samples', 0) > 0:
        print(f"\n💡 NEXT STEPS:")
        print("1. The rate limiting fix has been applied")
        print("2. Run the pilot script again with proper delays")
        print("3. It will automatically retry failed runs only")
        print("4. Expected time with fix: ~3 minutes for remaining samples")
    else:
        print("\n✅ All samples completed successfully!")


# Backwards compatibility
def main():
    """Main function for backwards compatibility."""
    analyze_gemini_2_5_results()


if __name__ == "__main__":
    main()
