# ACSES Pilot Study - Processing Pipeline Documentation

## Sequential Processing Steps

The scripts have been organized with sequential numbering to clearly show the processing pipeline steps:

### Phase 0: Setup and Validation
- **00_setup_and_validate.py** - Initial setup validation and environment checks

### Phase 1: Data Preparation  
- **01_prepare_codebook.py** - Transform KBLI codebook into hierarchical format

### Phase 2: Dataset Enhancement
- **02a_add_unique_ids.py** - Add UUID identifiers to test dataset
- **02b_test_rate_limiting.py** - Test API rate limiting before main execution

### Phase 3: Study Execution
- **03a_run_pilot_study.py** - Run main pilot study with single model
- **03b_run_multi_model_pilot.py** - Run comparative study across multiple models

### Phase 4: Analysis and Results
- **04a_analyze_results.py** - General results analysis and visualization
- **04b_analyze_gemini_2_5.py** - Specialized analysis for Gemini 2.5 results

## Processing Flow

```
00_setup_and_validate.py
         ↓
01_prepare_codebook.py
         ↓
02a_add_unique_ids.py
         ↓
02b_test_rate_limiting.py (optional validation)
         ↓
03a_run_pilot_study.py OR 03b_run_multi_model_pilot.py
         ↓
04a_analyze_results.py
         ↓  
04b_analyze_gemini_2_5.py (if using Gemini 2.5)
```

## Execution Order

1. **Setup Phase**: Run `00_setup_and_validate.py` to verify environment
2. **Data Prep**: Run `01_prepare_codebook.py` to create hierarchical codebook
3. **Dataset Enhancement**: Run `02a_add_unique_ids.py` to add tracking IDs
4. **Rate Test** (Optional): Run `02b_test_rate_limiting.py` to validate API limits
5. **Study Execution**: 
   - For single model: Run `03a_run_pilot_study.py`
   - For multi-model comparison: Run `03b_run_multi_model_pilot.py`
6. **Analysis**: Run `04a_analyze_results.py` for general analysis
7. **Specialized Analysis**: Run `04b_analyze_gemini_2_5.py` if needed

## Data Dependencies

- **Input**: `data/input/mini_test.csv`, `data/input/kbli_codebook.csv`
- **Intermediate**: `data/output/mini_test_with_ids.csv`, `data/output/kbli_codebook_hierarchical.csv`
- **Output**: `data/output/llm_results/*.jsonl`, analysis files in `data/output/`

## Notes

- Scripts are designed to be resumable where possible (JSONL format)
- Rate limiting is built into API calls
- UUID tracking enables robust data lineage
- All scripts include comprehensive error handling and logging
