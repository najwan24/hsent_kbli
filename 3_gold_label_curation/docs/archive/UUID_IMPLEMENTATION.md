# UUID Implementation for ACSES Pilot Study

## 🆔 Why Add UUIDs to Your Dataset?

Your request to add UUIDs is excellent! Here are the key advantages:

### 🎯 **Tracking & Identification**
- **Unique Global IDs**: Each sample has a globally unique identifier
- **No Confusion**: No reliance on row indices that can change
- **Cross-System Compatibility**: UUIDs work across different systems and processes

### 🔄 **Robust Resume Capability**
- **Perfect Tracking**: Resume exactly where you left off using UUID+run_number
- **Data Integrity**: No risk of processing the same sample twice
- **Audit Trail**: Complete history of which samples were processed when

### 📊 **Enhanced Analysis**
- **Data Lineage**: Track samples from raw data through processing to results
- **Debugging**: Easily find and analyze specific problematic samples
- **Merging**: Safely join data from different processing runs
- **Reproducibility**: Exact sample identification for research reproducibility

## 🛠️ Implementation Details

### **Script: `src/02a_add_unique_ids.py`**

**What it does:**
1. Loads your original `mini_test.csv`
2. Generates UUID4 for each sample (36-character unique ID)
3. Adds UUID as first column (`sample_id`)
4. Preserves all original data
5. Adds metadata columns for tracking
6. Saves as `mini_test_with_ids.csv`

**Output Format:**
```csv
sample_id,text,kbli_code,category,kbli_count,id_created_at,original_row_index
f47ac10b-58cc-4372-a567-0e02b2c3d479,"jagal sapi menghasilkan...",10110,C,71,2025-07-25T10:30:00,0
6ba7b810-9dad-11d1-80b4-00c04fd430c8,"bagian produksi membersihkan...",10120,C,108,2025-07-25T10:30:00,1
```

## 🔧 **Usage Instructions**

### Step 1: Generate UUIDs
```bash
# Option 1: Full script
python src/02a_add_unique_ids.py

# Option 2: Convenience script  
python src/add_ids.py
```

### Step 2: Run Pilot Study
```bash
# The pilot script automatically detects and uses the enhanced dataset
python src/03a_run_pilot_study.py
```

**Auto-Detection Logic:**
- ✅ First tries to load `mini_test_with_ids.csv` (enhanced)
- ⚠️ Falls back to `mini_test.csv` if enhanced not found
- 🔧 Generates temporary row-based IDs if no UUIDs available

## 📈 **Before vs After Comparison**

### **Before (Row-based IDs)**
```jsonl
{"sample_id": 0, "run_number": 1, "original_text": "jagal sapi..."}
{"sample_id": 1, "run_number": 1, "original_text": "bagian produksi..."}
```
**Problems:**
- ❌ Row indices change if data is reordered
- ❌ Hard to track across different data versions
- ❌ No global uniqueness guarantee

### **After (UUID-based)**
```jsonl
{"sample_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "run_number": 1, "original_text": "jagal sapi..."}
{"sample_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8", "run_number": 1, "original_text": "bagian produksi..."}
```
**Benefits:**
- ✅ Globally unique, never changes
- ✅ Works across different data versions
- ✅ Perfect for distributed processing
- ✅ Enables robust data lineage

## 🔍 **Enhanced Pilot Study Capabilities**

### **1. Robust Resume Logic**
```python
# Resume tracking now uses UUIDs
completed_runs = {
    ("f47ac10b-58cc-4372-a567-0e02b2c3d479", 1),  # UUID + run number
    ("f47ac10b-58cc-4372-a567-0e02b2c3d479", 2),
    ("6ba7b810-9dad-11d1-80b4-00c04fd430c8", 1),
    # ... etc
}
```

### **2. Enhanced Result Metadata**
```json
{
  "sample_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "original_row_index": 0,
  "sample_id_created_at": "2025-07-25T10:30:00",
  "run_number": 1,
  "is_correct": true,
  "confidence_score": 0.95,
  "reasoning": "...",
  "model_name": "gemini-1.5-flash-latest",
  "timestamp": "2025-07-25T14:45:22"
}
```

### **3. Better Analysis Capabilities**
- **Sample Tracking**: Find all runs for a specific sample by UUID
- **Cross-Run Analysis**: Compare results across different models for same sample
- **Error Investigation**: Quickly locate problematic samples for debugging
- **Temporal Analysis**: Track processing patterns over time

## 📊 **Real-World Benefits**

### **Scenario 1: Long-Running Job Interrupted**
```bash
# Day 1: Process 500 samples
Processing sample 500/2,268: 10130 (ID: f47ac10b-58cc-4372-a567-0e02b2c3d479)
  Run 1/3... ✅ [Saved]
  Run 2/3... ❌ Network timeout

# Day 2: Resume automatically
🔄 Checking for existing results...
📂 Found 1,501 existing results
Processing sample 500/2,268: 10130 (ID: f47ac10b-58cc-4372-a567-0e02b2c3d479) 
  📋 Need to complete runs: [2, 3]  # Exact resume point!
```

### **Scenario 2: Data Version Changes**
```bash
# Original mini_test.csv gets updated with new samples
# UUID-based results remain valid and can be merged safely
# No confusion about which results belong to which samples
```

### **Scenario 3: Multi-Model Analysis**
```python
# Easy to compare results for the same sample across models
flash_result = results[results['sample_id'] == 'f47ac10b...']['is_correct'].mean()
pro_result = results[results['sample_id'] == 'f47ac10b...']['is_correct'].mean()
```

## 🚀 **File Structure After Implementation**

```
3_gold_label_curation/
├── data/
│   ├── input/
│   │   ├── mini_test.csv                    # Original dataset
│   │   ├── mini_test_with_ids.csv          # Enhanced with UUIDs ⭐
│   │   └── dataset_with_ids_analysis.json  # Analysis of enhanced dataset
│   └── output/
│       └── pilot_results_*.jsonl           # Results with UUID tracking
├── src/
│   ├── 02a_add_unique_ids.py              # UUID generation script ⭐
│   ├── add_ids.py                         # Convenience runner ⭐
│   └── 03a_run_pilot_study.py             # Enhanced with UUID support ⭐
```

## ✅ **Validation & Quality Checks**

The UUID script includes comprehensive validation:

- **UUID Format Validation**: Ensures proper UUID4 format
- **Uniqueness Verification**: Confirms all IDs are unique
- **Data Integrity Checks**: Validates original data preservation
- **Completeness Verification**: Ensures no samples lost in process
- **Statistical Analysis**: Provides dataset distribution analysis

## 🎯 **Quick Start**

```bash
# 1. Generate UUIDs for your dataset
python src/02a_add_unique_ids.py

# 2. Run pilot study (automatically uses enhanced dataset)
python src/03a_run_pilot_study.py

# 3. Results now include robust UUID tracking!
```

## 📝 **Summary**

Adding UUIDs transforms your pilot study from a basic processing script into a **production-ready, enterprise-grade data processing system** with:

- 🛡️ **Zero data loss** risk
- 🔄 **Perfect resumption** capability  
- 📊 **Enhanced tracking** and analysis
- 🔍 **Better debugging** and troubleshooting
- 📈 **Scalable architecture** for larger datasets

This is exactly the kind of improvement that separates research code from production systems!
