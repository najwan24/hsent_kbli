# Code Documentation and API Reference

## Core Module Functions

### Data Preparation Module (`00_prepare_codebook.py`)

#### `load_kbli_codebook(filepath: str) -> pd.DataFrame`
Loads the KBLI codebook from CSV file.

**Parameters:**
- `filepath`: Path to the KBLI codebook CSV file

**Returns:**
- `pd.DataFrame`: Loaded codebook data

**Usage:**
```python
codebook = load_kbli_codebook("data/input/kbli_codebook.csv")
```

#### `create_hierarchical_structure(codebook: pd.DataFrame) -> pd.DataFrame`
Creates hierarchical structure from flat codebook.

**Parameters:**
- `codebook`: Original codebook DataFrame

**Returns:**
- `pd.DataFrame`: Hierarchical codebook with parent-child relationships

### UUID Generation Module (`02a_add_unique_ids.py`)

#### `generate_uuid_dataset(input_path: str, output_path: str) -> None`
Adds UUIDs to dataset for tracking.

**Parameters:**
- `input_path`: Path to input CSV file
- `output_path`: Path for output CSV with UUIDs

**Features:**
- Generates UUID4 for each row
- Preserves original data integrity
- Adds metadata columns

**Example Output:**
```csv
sample_id,text,kbli_code,category,kbli_count,id_created_at,original_row_index
f47ac10b-58cc-4372-a567-0e02b2c3d479,"jagal sapi...",10110,C,71,2025-07-25T10:30:00,0
```

### Pilot Study Module (`03a_run_pilot_study.py`)

#### `class PilotStudyRunner`

Main class for executing pilot studies with resume capability.

##### `__init__(self, model_name: str, num_runs: int = 5)`

**Parameters:**
- `model_name`: Gemini model identifier
- `num_runs`: Number of runs per sample (default: 5)

##### `load_existing_results(self, output_file: str) -> Set[Tuple[str, int]]`
Loads existing results to enable resume functionality.

**Parameters:**
- `output_file`: Path to JSONL results file

**Returns:**
- `Set[Tuple[str, int]]`: Set of completed (sample_id, run_number) pairs

##### `get_rate_limit_delay(self, model_name: str) -> float`
Calculates appropriate delay between API requests.

**Parameters:**
- `model_name`: Full model name

**Returns:**
- `float`: Delay in seconds between requests

**Rate Limit Configuration:**
```python
RPM_LIMITS = {
    "models/gemini-1.5-flash-latest": 15,
    "models/gemini-1.5-pro-latest": 2,
    "models/gemini-2.5-flash-lite": 15,
}
```

##### `make_api_request(self, prompt: str, sample_data: dict, run_number: int) -> dict`
Makes a single API request with error handling.

**Parameters:**
- `prompt`: Formatted prompt string
- `sample_data`: Dictionary containing sample information
- `run_number`: Current run number

**Returns:**
- `dict`: Result dictionary with success status and response data

**Result Format:**
```python
{
    "sample_id": str,
    "run_number": int,
    "model": str,
    "timestamp": str,
    "success": bool,
    "is_correct": bool,
    "confidence_score": float,
    "response_text": str,
    "error_message": str  # Only if success=False
}
```

##### `run_pilot_study(self, input_file: str, output_file: str) -> None`
Executes the complete pilot study.

**Parameters:**
- `input_file`: Path to input dataset CSV
- `output_file`: Path to output JSONL file

**Process:**
1. Load existing results for resume capability
2. Process each sample with specified number of runs
3. Apply rate limiting between requests
4. Save results immediately in JSONL format
5. Handle errors gracefully with retry logic

## Configuration Constants

### Model Configuration

```python
AVAILABLE_MODELS = [
    "models/gemini-1.5-flash-latest",
    "models/gemini-1.5-pro-latest", 
    "models/gemini-2.5-flash-lite"
]

RPM_LIMITS = {
    "models/gemini-1.5-flash-latest": 15,
    "models/gemini-1.5-pro-latest": 2,
    "models/gemini-2.5-flash-lite": 15,
}
```

### File Paths

```python
INPUT_PATHS = {
    "kbli_codebook": "data/input/kbli_codebook.csv",
    "test_dataset": "data/input/mini_test.csv",
    "test_with_ids": "data/input/mini_test_with_ids.csv"
}

OUTPUT_PATHS = {
    "hierarchical_codebook": "data/output/kbli_codebook_hierarchical.csv",
    "pilot_results": "data/output/pilot_results_{model}_{timestamp}.jsonl",
    "analysis_summary": "data/output/pilot_analysis_summary.json"
}
```

## Error Handling

### Exception Types

#### `APIError`
Raised when Gemini API returns an error.

**Common Causes:**
- Rate limit exceeded
- Invalid API key
- Malformed request

#### `ConfigurationError`
Raised when configuration is invalid.

**Common Causes:**
- Missing API key
- Invalid model name
- Missing input files

### Error Recovery Patterns

```python
try:
    result = make_api_request(prompt, sample_data, run_number)
except ResourceExhausted as e:
    # Handle rate limiting
    retry_delay = extract_retry_delay(str(e))
    time.sleep(retry_delay)
    continue
except Exception as e:
    # Log error and continue
    error_result = {
        "success": False,
        "error_message": str(e),
        "timestamp": datetime.now().isoformat()
    }
    save_result(error_result)
```

## Data Formats

### Input Data Format (CSV)

```csv
sample_id,text,kbli_code,category,kbli_count
f47ac10b-58cc-4372-a567-0e02b2c3d479,"job description text",10110,C,71
```

**Required Columns:**
- `sample_id`: Unique identifier (UUID format recommended)
- `text`: Job description text
- `kbli_code`: Expected KBLI classification code
- `category`: Business category
- `kbli_count`: Frequency count

### Output Data Format (JSONL)

Each line contains a complete result object:

```jsonl
{"sample_id": "uuid", "run_number": 1, "model": "gemini-1.5-flash-latest", "timestamp": "2025-01-15T10:30:00Z", "success": true, "is_correct": true, "confidence_score": 0.95, "response_text": "Classification: 10110\nConfidence: 95%", "processing_time": 2.3}
```

**Standard Fields:**
- `sample_id`: Sample identifier
- `run_number`: Run number (1-5 typically)
- `model`: Model used for classification
- `timestamp`: ISO format timestamp
- `success`: Boolean indicating successful API call
- `is_correct`: Boolean indicating correct classification
- `confidence_score`: Float 0-1 indicating model confidence
- `response_text`: Raw model response
- `processing_time`: Time in seconds for processing

**Error Fields (when success=False):**
- `error_message`: Description of error
- `error_type`: Type of error encountered
- `retry_count`: Number of retries attempted

## Utility Functions

### `load_prompt_template(template_path: str) -> str`
Loads the master prompt template.

### `format_prompt(template: str, job_description: str, codebook: str) -> str`
Formats the prompt with specific job description and codebook context.

### `extract_classification(response_text: str) -> Tuple[str, float]`
Extracts KBLI code and confidence score from model response.

### `validate_kbli_code(code: str, codebook: pd.DataFrame) -> bool` 
Validates that extracted KBLI code exists in codebook.

### `calculate_accuracy(results: List[dict]) -> dict`
Calculates accuracy metrics from results list.

## Usage Examples

### Basic Pilot Study

```python
from src.pilot_study_runner import PilotStudyRunner

# Initialize runner
runner = PilotStudyRunner(
    model_name="models/gemini-1.5-flash-latest",
    num_runs=5
)

# Run pilot study
runner.run_pilot_study(
    input_file="data/input/mini_test_with_ids.csv",
    output_file="data/output/pilot_results.jsonl"
)
```

### Multi-Model Comparison

```python
models = [
    "models/gemini-1.5-flash-latest",
    "models/gemini-1.5-pro-latest",
    "models/gemini-2.5-flash-lite"
]

for model in models:
    runner = PilotStudyRunner(model_name=model, num_runs=3)
    output_file = f"data/output/pilot_results_{model.split('/')[-1]}.jsonl"
    runner.run_pilot_study("data/input/mini_test_with_ids.csv", output_file)
```

### Resume Interrupted Study

```python
# Simply rerun the same command - resume is automatic
runner = PilotStudyRunner(model_name="models/gemini-1.5-flash-latest")
runner.run_pilot_study(
    input_file="data/input/mini_test_with_ids.csv",
    output_file="data/output/pilot_results.jsonl"  # Same file as before
)
```
