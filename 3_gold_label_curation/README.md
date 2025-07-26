# ACSES Pilot Study - Gold Label Curation

This module implements the ACSES (Automated Classification System Evaluation Study) pilot study to determine the best LLM for KBLI code validation using hierarchical prompting.

## High-Level Project Overview

The ACSES pilot study is designed to evaluate and compare different Gemini language models for automated job description classification using the Indonesian Standard Industrial Classification (KBLI) system. This robust, production-ready implementation ensures reliable data curation at scale.

### Key Features

- **Multi-Model Evaluation**: Compare Gemini Flash, Pro, and Flash Lite models
- **Hierarchical Classification**: Uses structured KBLI codebook for accurate classification
- **Robust Resume Capability**: Zero data loss with JSONL format and smart progress tracking
- **Production-Ready**: Handles API limits, network interruptions, and resource exhaustion gracefully
- **Comprehensive Analysis**: Full pipeline from data preparation to performance evaluation

### Research Objectives

1. **Model Performance Comparison**: Determine which Gemini model provides the highest accuracy for KBLI classification
2. **Reliability Assessment**: Evaluate consistency across multiple runs per sample
3. **Scalability Testing**: Validate approach for large-scale data curation
4. **Cost-Effectiveness**: Compare model performance vs. API costs

## Documentation Structure

For detailed information, see the organized documentation:

- **[Installation & Setup](docs/setup.md)**: Environment configuration and API setup
- **[Workflow Guide](docs/workflow.md)**: Step-by-step pipeline execution  
- **[API Reference](docs/api_reference.md)**: Code documentation and technical details

## Quick Start

1. **Setup Environment**: Follow [setup instructions](docs/setup.md)
2. **Run Pipeline**: Follow [workflow guide](docs/workflow.md)
3. **API Reference**: Check [code documentation](docs/api_reference.md)

## Directory Structure

```
3_gold_label_curation/
├── src/                           # 📚 Core library code (reusable modules)
│   ├── config.py                  # Centralized configuration management
│   ├── utils/                     # Common utilities and helpers
│   ├── api/                       # API client implementations
│   ├── pipeline/                  # Data processing pipeline components
│   └── analysis/                  # Analysis and evaluation modules
├── scripts/                       # � Executable entry points
│   ├── prepare_codebook.py        # Phase 1: Codebook preparation
│   ├── add_unique_ids.py          # Phase 2A: Add UUID identifiers
│   ├── run_pilot_study.py         # Phase 2B: Execute pilot study
│   ├── analyze_results.py         # Analysis and reporting
│   └── setup_and_validate.py     # Environment validation
├── docs/                          # �📚 Consolidated Documentation
│   ├── setup.md                   # Installation and environment setup
│   ├── workflow.md                # Step-by-step pipeline documentation  
│   └── api_reference.md           # Code documentation and API reference
├── data/
│   ├── input/                     # Input datasets and codebooks
│   └── output/                    # Generated results and analysis
├── notebooks/                     # Jupyter analysis notebooks
├── prompts/                       # LLM prompt templates
├── tests/                         # Unit and integration tests
├── requirements.txt               # Python dependencies
└── README.md                      # This overview file
```

## Implementation Highlights

### 🛡️ Robust & Resumable Architecture
- **JSONL Format**: Each API result saved immediately, never overwritten
- **Resume Anywhere**: If interrupted, just restart the script
- **Smart Progress Tracking**: Knows exactly which sample+run combinations are complete
- **Resource Exhaustion Safe**: Handles API quota limits gracefully

### 🔄 Production-Ready Features
- **Rate Limiting**: Automatic compliance with API limits
- **Error Handling**: Comprehensive error recovery and logging
- **UUID Tracking**: Unique identifiers for perfect data lineage
- **Multi-Model Support**: Compare different Gemini models systematically

## Key Benefits

### UUID Implementation Benefits
- 🆔 **Global Unique IDs**: Each sample has a globally unique identifier
- 🔄 **Robust Resume**: Perfect tracking with UUID+run_number combinations
- 🔗 **Data Lineage**: Complete traceability from raw data to results
- 🐛 **Enhanced Debugging**: Easy identification of problematic samples

### JSONL Architecture Benefits  
- 💾 **Zero Data Loss**: Each result saved immediately, never overwritten
- ⚡ **Resume Anywhere**: Interrupted processes continue exactly where they left off
- 🎯 **Smart Progress**: Automatic detection of completed sample+run combinations
- 🛡️ **Error Resilience**: Graceful handling of API limits and network issues

## Expected Outcomes

### Success Metrics
- **Accuracy Rate**: Target >90% for production readiness
- **Consensus Rate**: Target >60% unanimous agreement across runs
- **Reliability**: Consistent performance across different sample types

### Decision Framework
- Model selection based on accuracy, consistency, and cost-effectiveness
- Quality control thresholds derived from confidence calibration
- Scalability validation for full dataset processing

## Contact & Support

For detailed implementation guidance, refer to the comprehensive documentation in the `docs/` folder or the analysis notebooks for results interpretation.
