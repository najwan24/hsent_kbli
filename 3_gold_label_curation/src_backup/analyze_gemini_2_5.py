#!/usr/bin/env python3
"""
Quick analysis of Gemini 2.5 Flash Lite results.
"""
import json
import os
from collections import defaultdict

def analyze_gemini_2_5_results():
    """Analyze the current Gemini 2.5 Flash Lite results."""
    
    # Path to results
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    file_path = os.path.join(project_root, "data", "output", "pilot_results_models", "gemini_2.5_flash_lite.jsonl")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    if not results:
        print("📭 No results found")
        return
    
    print(f"📊 GEMINI 2.5 FLASH LITE ANALYSIS")
    print("=" * 50)
    
    # Basic stats
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"📋 Total entries: {len(results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📈 Success rate: {len(successful) / len(results) * 100:.1f}%")
    
    # Sample coverage
    samples = set(r.get('sample_id', 'unknown') for r in results)
    print(f"🆔 Unique samples processed: {len(samples)}")
    
    # Run coverage per sample
    sample_runs = defaultdict(set)
    successful_sample_runs = defaultdict(set)
    
    for result in results:
        sample_id = result.get('sample_id', 'unknown')
        run_num = result.get('run_number', 0)
        sample_runs[sample_id].add(run_num)
        
        if result.get('success', False):
            successful_sample_runs[sample_id].add(run_num)
    
    # Check completeness
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
    
    print(f"✅ Complete samples: {len(complete_samples)}")
    print(f"⚠️  Incomplete samples: {len(incomplete_samples)}")
    
    # Error analysis
    if failed:
        rate_errors = [r for r in failed if 'ResourceExhausted' in r.get('error_type', '')]
        other_errors = [r for r in failed if 'ResourceExhausted' not in r.get('error_type', '')]
        
        print(f"\n❌ ERROR BREAKDOWN:")
        print(f"• Rate limit errors: {len(rate_errors)}")
        print(f"• Other errors: {len(other_errors)}")
        
        if rate_errors:
            print(f"\n⚠️  RATE LIMITING ISSUE DETECTED:")
            print(f"• The script was making requests too fast")
            print(f"• Gemini 2.5 Flash Lite limit: 15 requests per minute")
            print(f"• Required delay: 4+ seconds between requests")
            print(f"• Current delay was: 1 second (too fast!)")
    
    # Show which samples need retry
    if incomplete_samples:
        print(f"\n🔄 SAMPLES NEEDING RETRY:")
        for sample_id, missing_runs in incomplete_samples[:3]:
            print(f"• {sample_id[:8]}... missing runs: {sorted(missing_runs)}")
        if len(incomplete_samples) > 3:
            print(f"• ... and {len(incomplete_samples) - 3} more")
    
    print(f"\n💡 NEXT STEPS:")
    if incomplete_samples:
        print("1. The rate limiting fix has been applied")
        print("2. Run the pilot script again with proper delays")
        print("3. It will automatically retry failed runs only")
        print("4. Expected time with fix: ~3 minutes for remaining samples")
    else:
        print("✅ All samples completed successfully!")

if __name__ == "__main__":
    analyze_gemini_2_5_results()
