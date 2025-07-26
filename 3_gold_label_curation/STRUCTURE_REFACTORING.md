# ACSES Project Structure Refactoring

## 📁 New Project Structure

The ACSES project has been refactored to follow Python best practices with clear separation between library code and executable scripts.

### Directory Structure

```
3_gold_label_curation/
├── src/                          # 📚 Core library code
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Centralized configuration
│   ├── utils/                   # Utility modules
│   │   ├── __init__.py
│   │   └── common.py           # Common utilities
│   ├── api/                     # API clients
│   │   ├── __init__.py
│   │   └── gemini_client.py    # Gemini API wrapper
│   ├── pipeline/                # Data processing pipeline
│   │   ├── __init__.py
│   │   ├── codebook_processor.py
│   │   ├── dataset_enhancer.py
│   │   └── pilot_runner.py
│   └── analysis/                # Analysis modules
│       ├── __init__.py
│       └── result_analyzer.py
├── scripts/                     # 🚀 Executable scripts
│   ├── prepare_codebook.py      # Phase 1: Codebook preparation
│   ├── add_unique_ids.py        # Phase 2A: Add UUIDs
│   ├── run_pilot_study.py       # Phase 2B: Run pilot study
│   ├── run_multi_model_pilot.py # Phase 2C: Multi-model comparison
│   ├── analyze_results.py       # Analysis script
│   └── setup_and_validate.py    # Setup validation
├── tests/                       # Unit and integration tests
├── data/                        # Data files (unchanged)
├── docs/                        # Documentation (unchanged)
├── notebooks/                   # Jupyter notebooks (unchanged)
└── migrate_structure.py         # Migration helper script
```

## 🔄 Migration Process

### Step 1: Run Migration Script
```bash
cd 3_gold_label_curation
python migrate_structure.py
```

### Step 2: Update Documentation
The documentation in `docs/` folder already follows the new structure and provides clear guidance for users.

### Step 3: Test New Structure
```bash
# Test codebook preparation
python scripts/prepare_codebook.py

# Test UUID addition
python scripts/add_unique_ids.py

# Test pilot study
python scripts/run_pilot_study.py
```

## 🎯 Benefits of New Structure

### 1. **Clear Separation of Concerns**
- **Library code** (`src/`): Reusable classes and functions
- **Scripts** (`scripts/`): Command-line interfaces and entry points
- **Tests** (`tests/`): Isolated testing framework

### 2. **Improved Maintainability**
- Centralized configuration in `src/config.py`
- Common utilities shared across modules
- Consistent error handling and logging

### 3. **Better Testability**
- Core logic can be unit tested independently
- Scripts become thin wrappers around library functions
- Easy to mock dependencies

### 4. **Professional Standards**
- Follows Python packaging conventions
- Easier to convert to installable package
- Clear entry points for users

## 📋 Usage Examples

### Using Scripts (Recommended for Users)
```bash
# Prepare codebook
python scripts/prepare_codebook.py

# Add UUIDs to dataset
python scripts/add_unique_ids.py

# Run pilot study
python scripts/run_pilot_study.py --model gemini-1.5-flash-latest --runs 3
```

### Using Library Code (For Developers)
```python
from src.config import CONFIG, PATHS
from src.pipeline.codebook_processor import CodebookProcessor

# Initialize processor
processor = CodebookProcessor(
    input_path=PATHS.kbli_codebook,
    output_path=PATHS.hierarchical_codebook
)

# Process codebook
success = processor.process()
```

## 🧪 Testing Strategy

### Unit Tests
```bash
# Test individual components
python -m pytest tests/test_codebook_processor.py
python -m pytest tests/test_dataset_enhancer.py
```

### Integration Tests
```bash
# Test complete pipeline
python -m pytest tests/test_pipeline_integration.py
```

## 📚 Next Steps

1. Complete migration of all existing scripts
2. Add comprehensive error handling
3. Implement unit tests for all modules
4. Add command-line argument parsing to scripts
5. Create installable package setup

This structure provides a solid foundation for maintaining and extending the ACSES pilot study codebase.
