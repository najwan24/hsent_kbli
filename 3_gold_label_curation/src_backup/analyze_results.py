#!/usr/bin/env python3
"""
Analyze pilot study results from JSONL file.
"""
import json
import os
from collections import defaultdict, Counter

def analyze_pilot_results(jsonl_path: str):
    """
    Analyze the pilot study results and show statistics.
    
    Args:
        jsonl_path: Path to the JSONL results file
    """
    if not os.path.exists(jsonl_path):
        print(f"❌ File not found: {jsonl_path}")
        return
    
    results = []
    
    # Load all results
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    result = json.loads(line)
                    results.append(result)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Warning: Invalid JSON on line {line_num}: {e}")
                    continue
    
    if not results:
        print("📭 No results found in file")
        return
    
    print(f"📊 PILOT STUDY RESULTS ANALYSIS")
    print(f"📁 File: {jsonl_path}")
    print(f"📋 Total entries: {len(results)}")
    print("=" * 60)
    
    # Basic statistics
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"\n🎯 SUCCESS RATE:")
    print(f"✅ Successful runs: {len(successful)}")
    print(f"❌ Failed runs: {len(failed)}")
    print(f"📈 Success rate: {len(successful) / len(results) * 100:.1f}%")
    
    # Sample coverage
    sample_runs = defaultdict(set)
    for result in results:
        sample_id = result.get('sample_id', 'unknown')
        run_num = result.get('run_number', 0)
        sample_runs[sample_id].add(run_num)
    
    print(f"\n📋 SAMPLE COVERAGE:")
    print(f"🆔 Unique samples: {len(sample_runs)}")
    
    # Check which samples have incomplete runs
    expected_runs = {1, 2, 3}  # Assuming 3 runs per sample
    incomplete_samples = []
    successful_sample_runs = defaultdict(set)
    
    for result in successful:
        sample_id = result.get('sample_id', 'unknown')
        run_num = result.get('run_number', 0)
        successful_sample_runs[sample_id].add(run_num)
    
    for sample_id, runs in sample_runs.items():
        successful_runs = successful_sample_runs.get(sample_id, set())
        if successful_runs != expected_runs:
            missing_runs = expected_runs - successful_runs
            incomplete_samples.append((sample_id, missing_runs))
    
    if incomplete_samples:
        print(f"⚠️  Samples with incomplete successful runs: {len(incomplete_samples)}")
        print("   (These will be retried on resume)")
        for sample_id, missing_runs in incomplete_samples[:5]:  # Show first 5
            print(f"   • {sample_id}: missing runs {sorted(missing_runs)}")
        if len(incomplete_samples) > 5:
            print(f"   ... and {len(incomplete_samples) - 5} more")
    else:
        print("✅ All samples have complete successful runs")
    
    # Error analysis
    if failed:
        print(f"\n❌ ERROR ANALYSIS:")
        error_types = Counter(r.get('error_type', 'Unknown') for r in failed)
        for error_type, count in error_types.most_common():
            print(f"• {error_type}: {count} occurrences")
        
        # Show some error messages
        resource_exhausted = [r for r in failed if 'ResourceExhausted' in r.get('error_type', '')]
        if resource_exhausted:
            print(f"\n⚠️  ResourceExhausted errors: {len(resource_exhausted)}")
            print("   These will be automatically retried when you resume the script")
    
    # Model performance
    models = Counter(r.get('model_name', 'Unknown') for r in results)
    print(f"\n🤖 MODELS USED:")
    for model, count in models.items():
        success_count = len([r for r in results if r.get('model_name') == model and r.get('success', False)])
        success_rate = success_count / count * 100 if count > 0 else 0
        print(f"• {model}: {count} runs ({success_rate:.1f}% success)")
    
    # Processing time analysis
    if successful:
        processing_times = [r.get('processing_time_seconds', 0) for r in successful]
        avg_time = sum(processing_times) / len(processing_times)
        print(f"\n⏱️  PERFORMANCE:")
        print(f"• Average processing time: {avg_time:.2f} seconds")
        print(f"• Total processing time: {sum(processing_times):.1f} seconds")
    
    print(f"\n💡 NEXT STEPS:")
    if failed:
        print("• Run the pilot script again to retry failed requests")
        print("• Failed runs will be automatically retried")
    else:
        print("• All runs completed successfully!")
        print("• You can now run analysis on the complete dataset")

def main():
    """Main function."""
    # Find the results file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, "data", "output")
    
    # Look for JSONL files
    jsonl_files = [f for f in os.listdir(output_dir) if f.endswith('.jsonl') and 'pilot_results' in f]
    
    if not jsonl_files:
        print("❌ No pilot results files found in data/output/")
        return
    
    if len(jsonl_files) == 1:
        jsonl_path = os.path.join(output_dir, jsonl_files[0])
        analyze_pilot_results(jsonl_path)
    else:
        print("📁 Multiple results files found:")
        for i, filename in enumerate(jsonl_files, 1):
            print(f"  {i}. {filename}")
        
        try:
            choice = int(input("\nSelect file to analyze (number): ")) - 1
            if 0 <= choice < len(jsonl_files):
                jsonl_path = os.path.join(output_dir, jsonl_files[choice])
                analyze_pilot_results(jsonl_path)
            else:
                print("❌ Invalid choice")
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Cancelled")

if __name__ == "__main__":
    main()
