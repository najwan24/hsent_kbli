#!/usr/bin/env python3

from src.analysis.results_analyzer import ResultsAnalyzer
from pathlib import Path

analyzer = ResultsAnalyzer()
print(f"Output dir: {analyzer.output_dir}")

model_name = "gemini_2.5_flash_lite"
transformed_name = model_name.replace("-", "_").replace(".", "_")
print(f"Model name: {model_name}")
print(f"Transformed name: {transformed_name}")

expected_path = analyzer.output_dir / "pilot_results_models" / f"models_{transformed_name}_mini_test_with_ids.jsonl"
print(f"Expected path: {expected_path}")
print(f"Path exists: {expected_path.exists()}")

# List actual files
models_dir = analyzer.output_dir / "pilot_results_models"
if models_dir.exists():
    print(f"\nActual files in {models_dir}:")
    for file in models_dir.iterdir():
        print(f"  {file.name}")
