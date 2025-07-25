# ACSES Pilot Study - Gold Label Curation

This module implements the ACSES (Automated Classification System Evaluation Study) pilot study to determine the best LLM for KBLI code validation using hierarchical prompting.

## Overview

The pilot study evaluates different Gemini models (Flash vs Pro) on a subset of job descriptions to determine which model provides the most reliable and accurate KBLI code validation for full-scale data curation.

## 🛡️ Robust & Resumable Implementation

This implementation uses **JSONL format** and **resume capability** to ensure zero data loss:

- **✅ Never Lose Progress**: Each API result saved immediately, never overwritten
- **✅ Resume Anywhere**: If interrupted (power, network, API limits), just restart the script
- **✅ Smart Progress Tracking**: Knows exactly which sample+run combinations are complete  
- **✅ Resource Exhaustion Safe**: Handles API quota limits gracefully
- **✅ Production Ready**: Designed for long-running, mission-critical data curation

> **Why JSONL?** Unlike JSON arrays that must be rewritten entirely, JSONL appends each result as a new line. This means your progress is never lost, even during unexpected interruptions.

## Directory Structure

```
3_gold_label_curation/
├── data/
│   ├── input/
│   │   ├── kbli_codebook.csv      # Original KBLI codebook
│   │   └── mini_test.csv          # Test dataset for pilot
│   ├── output/
│       ├── kbli_codebook_hierarchical.csv  # Processed hierarchical codebook
│       ├── pilot_results_*.jsonl           # Pilot study results (JSONL format)
│       └── pilot_analysis_summary.json     # Analysis summary
├── notebooks/
│   └── analyze_pilot.ipynb        # Analysis and comparison notebook
├── prompts/
│   └── master_prompt.txt          # LLM prompt template
├── src/
│   ├── 00_prepare_codebook.py     # Phase 1: Codebook preparation
│   ├── 03a_run_pilot_study.py     # Phase 2: Single model pilot
│   └── 03b_run_multi_model_pilot.py # Phase 2: Multi-model comparison
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
└── README.md                      # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd 3_gold_label_curation
pip install -r requirements.txt
```

### 2. Configure API Access

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Load Environment Variables (if using .env file)

```bash
# For PowerShell
Get-Content .env | ForEach-Object { 
    $key, $value = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($key, $value, "Process")
}

# Or set directly in PowerShell
$env:GEMINI_API_KEY="your_actual_api_key_here"
```

## Execution Workflow

### Phase 1: Prepare Hierarchical Codebook

Transform the KBLI codebook into a hierarchical format suitable for LLM prompts:

```bash
python src/00_prepare_codebook.py
```

**What it does:**
- Loads `data/input/kbli_codebook.csv`
- Creates hierarchical structure for 5-digit codes
- Outputs `data/output/kbli_codebook_hierarchical.csv`

### Phase 2A: Add Unique IDs (Recommended)

Add UUID identifiers to your dataset for better tracking:

```bash
python src/02a_add_unique_ids.py
# Or use the convenience script:
python src/add_ids.py
```

**What it does:**
- Adds UUID column to `mini_test.csv`
- Creates `mini_test_with_ids.csv` with unique identifiers
- Enables robust tracking across interruptions and analyses
- Improves data lineage and debugging capabilities

**Benefits of UUIDs:**
- 🔍 Better tracking in distributed processing
- 📊 Robust data lineage and audit trails  
- 🔄 Enables safe resumption and error recovery
- 🔗 Facilitates data merging and analysis
- 🐛 Improved debugging and reproducibility

### Phase 2B: Run Pilot Study

#### Option A: Single Model Pilot

```bash
python src/03a_run_pilot_study.py
```

**Configuration options** (edit the script):
- `MODEL_NAME`: Choose between "gemini-1.5-flash-latest" or "gemini-1.5-pro-latest"
- `N_RUNS`: Number of runs per sample (default: 3)
- `TEMPERATURE`: Generation temperature (default: 0.7)

#### Option B: Multi-Model Comparison

```bash
python src/03b_run_multi_model_pilot.py
```

**What it does:**
- Runs pilot study for both Flash and Pro models
- Automatically manages model switching
- Saves separate result files for each model
- Provides comprehensive comparison

### Phase 3: Analysis

Open and run the analysis notebook:

```bash
jupyter notebook notebooks/analyze_pilot.ipynb
```

**Analysis includes:**
1. **Success Rate**: API call reliability by model
2. **Reasoning Quality**: Manual inspection of LLM reasoning
3. **Confidence Calibration**: How well confidence scores predict correctness
4. **Consensus Analysis**: Agreement across multiple runs per sample

## Key Files Explained

### Input Files

- **`kbli_codebook.csv`**: Original Indonesian Standard Industrial Classification codebook
- **`mini_test.csv`**: Test dataset with columns:
  - `text`: Job description text
  - `kbli_code`: Assigned 5-digit KBLI code
  - `category`: Category letter
  - `kbli_count`: Frequency count

### Generated Files

- **`kbli_codebook_hierarchical.csv`**: Hierarchical codebook with columns:
  - `code_5`, `title_5`, `desc_5`: Sub-class level
  - `code_4`, `title_4`: Class level
  - `code_3`, `title_3`: Group level
  - `code_2`, `title_2`: Division level
  - `code_1`, `title_1`: Section level

- **`pilot_results_*.json`**: Results with metadata:
  - `is_correct`: LLM's correctness judgment
  - `confidence_score`: Confidence level (0.0-1.0)
  - `reasoning`: Detailed explanation
  - `alternative_codes`: Suggested alternatives if incorrect
  - Sample metadata and processing information

## Expected Outputs

### Success Metrics
- **Success Rate**: >90% for production readiness
- **Consensus Rate**: >60% unanimous agreement across runs
- **Confidence Calibration**: Higher confidence for correct predictions

### Decision Criteria
- Choose model with highest success rate and best reasoning quality
- Consider cost-performance trade-offs (Flash vs Pro)
- Evaluate consensus patterns for quality control implementation

## Troubleshooting

### Common Issues

1. **API Key Error**:
   ```
   ValueError: GEMINI_API_KEY environment variable not found
   ```
   **Solution**: Ensure your API key is properly set in environment variables

2. **Missing Hierarchical Codebook**:
   ```
   FileNotFoundError: Hierarchical codebook not found
   ```
   **Solution**: Run `python src/00_prepare_codebook.py` first

3. **JSON Parsing Errors**:
   - Check API rate limits
   - Verify prompt template formatting
   - Review model temperature settings

4. **Low Success Rate**:
   - Reduce temperature for more consistent outputs
   - Adjust prompt template for clearer instructions
   - Check input data quality

### Performance Optimization

- **Batch Processing**: Process in chunks for large datasets
- **Rate Limiting**: Add delays between API calls
- **Error Recovery**: Implement retry logic for failed calls
- **Parallel Processing**: Use multiple workers for different samples (not implemented)

## Next Steps

After completing the pilot study:

1. **Model Selection**: Choose optimal model based on analysis results
2. **Prompt Refinement**: Improve prompts based on error patterns
3. **Scale-Up**: Apply chosen configuration to full dataset
4. **Quality Control**: Implement confidence-based filtering
5. **Production Deployment**: Integrate into full ACSES pipeline

## Configuration Parameters

Key parameters to tune based on pilot results:

- **N_RUNS**: Increase for better consensus (trade-off: cost/time)
- **TEMPERATURE**: Lower for consistency, higher for creativity
- **CONFIDENCE_THRESHOLD**: Set minimum confidence for auto-approval
- **PROMPT_TEMPLATE**: Adjust based on reasoning quality analysis

## Cost Estimation

Rough cost estimates for different scales:
- Pilot (2,268 samples × 3 runs): ~7K API calls
- Full dataset estimate: Scale accordingly
- Consider Flash vs Pro pricing differences

---

## Contact & Support

For questions about the ACSES pilot study implementation, refer to the project documentation or analysis results in the notebook.
