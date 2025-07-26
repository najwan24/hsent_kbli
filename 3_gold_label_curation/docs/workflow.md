# Step-by-Step Pipeline Documentation

## 1. Data Preparation Pipeline

### Phase 1: Prepare Hierarchical Codebook

The first step transforms the KBLI codebook into a hierarchical format suitable for LLM processing.

**Script:** `scripts/01_prepare_codebook.py`

**Input:**
- `data/input/kbli_codebook.csv` - Original KBLI codebook

**Process:**
1. Loads the original KBLI codebook
2. Creates hierarchical structure for 5-digit codes
3. Organizes codes by category levels
4. Formats for LLM prompt integration

**Output:**
- `data/output/kbli_codebook_hierarchical.csv` - Hierarchical codebook

**Command:**
```bash
python scripts/01_prepare_codebook.py
```

### Phase 2: Add Unique Identifiers (Recommended)

This step adds UUID identifiers to your dataset for robust tracking and resume capability.

**Script:** `scripts/02a_add_unique_ids.py`

**Input:**
- `data/input/mini_test.csv` - Test dataset

**Process:**
1. Generates UUID4 for each sample (36-character unique ID)
2. Adds UUID as first column (`sample_id`)
3. Preserves all original data
4. Adds metadata columns for tracking

**Output:**
- `data/input/mini_test_with_ids.csv` - Dataset with unique identifiers

**Command:**
```bash
python scripts/02a_add_unique_ids.py
```

## 2. Analysis Workflow

### Single Model Pilot Study

For testing a single model configuration:

**Script:** `scripts/03a_run_pilot_study.py`

**Process:**
1. Loads hierarchical codebook and test dataset
2. Generates prompts using the master template
3. Makes API calls to specified Gemini model
4. Implements resume capability with JSONL format
5. Handles rate limiting automatically

**Command:**
```bash
python scripts/03a_run_pilot_study.py
```

### Multi-Model Comparison

For comparing multiple models simultaneously:

**Script:** `scripts/03b_run_multi_model_pilot.py`

**Features:**
- Parallel model evaluation
- Consistent test conditions
- Comparative analysis output
- Resource-aware execution

**Command:**
```bash
python scripts/03b_run_multi_model_pilot.py
```

## 3. Validation Procedures

### Resume Logic Validation

The system implements robust resume capability:

1. **Startup Check:** Script loads existing JSONL file (if any)
2. **Progress Tracking:** Identifies completed sample_id + run_number combinations
3. **Smart Skipping:** Only processes missing runs
4. **Immediate Saving:** Each API call result is saved instantly

### Rate Limiting Compliance

Automatic rate limiting ensures API compliance:

```python
RPM_LIMITS = {
    "models/gemini-1.5-flash-latest": 15,
    "models/gemini-1.5-pro-latest": 2,
    "models/gemini-2.5-flash-lite": 15,
}
```

### Data Integrity Checks

1. **UUID Uniqueness:** Verified during ID generation
2. **JSONL Format:** Each line validated as proper JSON
3. **Success Tracking:** Only successful runs marked as complete
4. **Error Logging:** All failures recorded for analysis

## 4. Output Generation

### JSONL Results Format

Each result is saved as a single line in JSONL format:

```jsonl
{"sample_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "run_number": 1, "model": "gemini-1.5-flash-latest", "timestamp": "2025-01-15T10:30:00Z", "is_correct": true, "confidence_score": 0.95, "response_text": "...", "success": true}
```

### Analysis Outputs

The pipeline generates several analysis files:

1. **Raw Results:** `pilot_results_[model]_[timestamp].jsonl`
2. **Analysis Summary:** `pilot_analysis_summary.json`
3. **Performance Metrics:** Generated via Jupyter notebooks
4. **Model Comparisons:** Cross-model evaluation reports

### Directory Structure After Execution

```
data/output/
├── kbli_codebook_hierarchical.csv
├── pilot_results_gemini_1.5_flash_latest.jsonl
├── pilot_analysis_summary.json
├── final/
│   └── consolidated_results.json
├── llm_results/
│   ├── model_performance.csv
│   └── error_analysis.json
└── pilot_results_models/
    ├── gemini_1.5_flash.jsonl
    ├── gemini_1.5_pro.jsonl
    └── gemini_2.5_flash_lite.jsonl
```

## 5. Troubleshooting Guide

### Common Issues and Solutions

#### 1. ResourceExhausted Errors

**Problem:** API quota exceeded
**Solution:** 
- Wait for quota reset
- Resume script will continue automatically
- Check rate limiting configuration

#### 2. Resume Not Working

**Problem:** Script reprocesses completed samples
**Solution:**
- Verify JSONL file format
- Check UUID consistency
- Ensure only successful runs marked complete

#### 3. Rate Limiting Issues

**Problem:** Still getting rate limit errors
**Solution:**
- Verify delay calculations
- Check model-specific RPM limits  
- Add additional buffer time

#### 4. Memory Issues

**Problem:** Script crashes with large datasets
**Solution:**
- JSONL format minimizes memory usage
- Process in smaller batches if needed
- Monitor system resources

### Error Recovery Procedures

1. **Identify Issue:** Check error logs in JSONL files
2. **Verify Environment:** Ensure API keys and dependencies are correct
3. **Resume Execution:** Simply restart the script
4. **Monitor Progress:** Check completion status regularly

### Performance Optimization

1. **Batch Processing:** Group similar requests
2. **Rate Limit Optimization:** Use maximum allowed request rate
3. **Resource Monitoring:** Track API usage and quotas
4. **Parallel Processing:** Use multi-model scripts when appropriate

### Quality Assurance

1. **Regular Validation:** Verify results during execution
2. **Consistency Checks:** Compare results across runs
3. **Error Analysis:** Review failed requests
4. **Performance Metrics:** Monitor accuracy and completion rates
