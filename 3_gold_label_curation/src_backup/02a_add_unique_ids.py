"""
ACSES Pilot Study - Phase 2A: Add Unique IDs to Dataset
This script adds UUID identifiers to the mini_test.csv dataset for better tracking and analysis.

Advantages of using UUIDs:
1. Unique identification across systems and datasets
2. Better tracking in distributed processing
3. Prevents confusion with row indices
4. Enables robust data lineage and audit trails
5. Facilitates merging and joining datasets
6. Improves reproducibility and debugging
"""

import pandas as pd
import uuid
import os
from datetime import datetime
from pathlib import Path

# --- Load .env file if present ---
try:
    from dotenv import load_dotenv
    dotenv_path = Path(__file__).parent.parent / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        print(f"✅ Loaded environment variables from {dotenv_path}")
except ImportError:
    print("⚠️  python-dotenv not installed. Continuing without .env support.")

def generate_unique_id() -> str:
    """
    Generate a unique identifier for each sample.
    Using UUID4 for maximum uniqueness and no predictability.
    
    Returns:
        String representation of UUID4
    """
    return str(uuid.uuid4())

def add_uuids_to_dataset(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Add UUID column to the dataset.
    
    Args:
        input_path: Path to the original mini_test.csv
        output_path: Path where the enhanced dataset will be saved
        
    Returns:
        Enhanced DataFrame with UUID column
    """
    print("📂 Loading original dataset...")
    
    # Load the original dataset
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    df = pd.read_csv(input_path, dtype={'kbli_code': str})
    original_count = len(df)
    
    print(f"✅ Loaded {original_count} samples from {os.path.basename(input_path)}")
    print(f"📊 Columns: {list(df.columns)}")
    
    # Add UUID column as the first column
    print("\n🔄 Generating unique IDs...")
    
    # Generate UUIDs for all rows
    uuids = [generate_unique_id() for _ in range(len(df))]
    
    # Insert UUID as the first column
    df.insert(0, 'sample_id', uuids)
    
    print(f"✅ Generated {len(uuids)} unique IDs")
    
    # Verify uniqueness (should always be true for UUID4, but good to check)
    unique_count = df['sample_id'].nunique()
    if unique_count != len(df):
        print(f"⚠️  Warning: Expected {len(df)} unique IDs, got {unique_count}")
    else:
        print(f"✅ All {unique_count} IDs are unique")
    
    # Add metadata columns for tracking
    df['id_created_at'] = datetime.now().isoformat()
    df['original_row_index'] = range(len(df))  # Preserve original ordering
    
    # Save the enhanced dataset
    print(f"\n💾 Saving enhanced dataset to {os.path.basename(output_path)}...")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✅ Enhanced dataset saved with {len(df)} rows and {len(df.columns)} columns")
    
    return df

def validate_enhanced_dataset(df: pd.DataFrame) -> bool:
    """
    Validate the enhanced dataset for quality and completeness.
    
    Args:
        df: Enhanced DataFrame to validate
        
    Returns:
        True if validation passes, False otherwise
    """
    print("\n🔍 VALIDATING ENHANCED DATASET")
    print("=" * 50)
    
    validation_passed = True
    
    # Check for required columns
    required_columns = ['sample_id', 'text', 'kbli_code', 'category', 'kbli_count']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        validation_passed = False
    else:
        print(f"✅ All required columns present: {required_columns}")
    
    # Check UUID format and uniqueness
    if 'sample_id' in df.columns:
        # Check for null UUIDs
        null_ids = df['sample_id'].isnull().sum()
        if null_ids > 0:
            print(f"❌ Found {null_ids} null sample IDs")
            validation_passed = False
        else:
            print("✅ No null sample IDs")
        
        # Check UUID format (basic check - should be 36 characters with hyphens)
        invalid_uuids = df[~df['sample_id'].str.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', na=False)]
        if len(invalid_uuids) > 0:
            print(f"❌ Found {len(invalid_uuids)} invalid UUID formats")
            print(f"   Examples: {invalid_uuids['sample_id'].head(3).tolist()}")
            validation_passed = False
        else:
            print("✅ All sample IDs have valid UUID format")
        
        # Check uniqueness
        duplicate_ids = df[df['sample_id'].duplicated()]
        if len(duplicate_ids) > 0:
            print(f"❌ Found {len(duplicate_ids)} duplicate sample IDs")
            validation_passed = False
        else:
            print("✅ All sample IDs are unique")
    
    # Check data integrity
    if 'text' in df.columns:
        empty_texts = df['text'].isnull().sum()
        if empty_texts > 0:
            print(f"⚠️  Warning: {empty_texts} samples have empty text")
        else:
            print("✅ All samples have text content")
    
    if 'kbli_code' in df.columns:
        empty_codes = df['kbli_code'].isnull().sum()
        if empty_codes > 0:
            print(f"⚠️  Warning: {empty_codes} samples have empty KBLI codes")
        else:
            print("✅ All samples have KBLI codes")
    
    # Summary statistics
    print(f"\n📊 DATASET SUMMARY:")
    print(f"   Total samples: {len(df)}")
    print(f"   Unique KBLI codes: {df['kbli_code'].nunique() if 'kbli_code' in df.columns else 'N/A'}")
    print(f"   Categories: {df['category'].nunique() if 'category' in df.columns else 'N/A'}")
    print(f"   Average text length: {df['text'].str.len().mean():.0f} characters" if 'text' in df.columns else "")
    
    return validation_passed

def create_sample_analysis(df: pd.DataFrame, output_dir: str) -> None:
    """
    Create a sample analysis file showing the distribution and examples.
    
    Args:
        df: Enhanced DataFrame
        output_dir: Directory to save analysis files
    """
    print("\n📈 CREATING SAMPLE ANALYSIS")
    print("=" * 50)
    
    analysis_data = {
        'dataset_info': {
            'total_samples': len(df),
            'total_columns': len(df.columns),
            'created_at': datetime.now().isoformat(),
            'columns': list(df.columns)
        },
        'sample_distribution': {
            'by_category': df['category'].value_counts().to_dict() if 'category' in df.columns else {},
            'by_kbli_prefix': df['kbli_code'].str[:2].value_counts().head(10).to_dict() if 'kbli_code' in df.columns else {},
            'text_length_stats': {
                'mean': float(df['text'].str.len().mean()) if 'text' in df.columns else 0,
                'median': float(df['text'].str.len().median()) if 'text' in df.columns else 0,
                'min': int(df['text'].str.len().min()) if 'text' in df.columns else 0,
                'max': int(df['text'].str.len().max()) if 'text' in df.columns else 0
            }
        },
        'sample_examples': df.head(5).to_dict('records') if len(df) > 0 else []
    }
    
    # Save analysis
    analysis_path = os.path.join(output_dir, 'dataset_with_ids_analysis.json')
    
    import json
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sample analysis saved to {os.path.basename(analysis_path)}")
    
    # Display key statistics
    print(f"\n📊 Key Statistics:")
    if 'category' in df.columns:
        print(f"   Most common category: {df['category'].mode().iloc[0]} ({df['category'].value_counts().iloc[0]} samples)")
    if 'kbli_code' in df.columns:
        print(f"   Most common KBLI prefix: {df['kbli_code'].str[:2].mode().iloc[0]} ({df['kbli_code'].str[:2].value_counts().iloc[0]} samples)")
    if 'text' in df.columns:
        print(f"   Text length range: {df['text'].str.len().min()} - {df['text'].str.len().max()} characters")

def main():
    """Main function to add UUIDs to the dataset."""
    print("🔧 ACSES Pilot Study - Adding Unique IDs to Dataset")
    print("=" * 60)
    
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    input_path = os.path.join(project_root, "data", "input", "mini_test.csv")
    output_path = os.path.join(project_root, "data", "input", "mini_test_with_ids.csv")
    output_dir = os.path.dirname(output_path)
    
    try:
        # Add UUIDs to dataset
        enhanced_df = add_uuids_to_dataset(input_path, output_path)
        
        # Validate the enhanced dataset
        if validate_enhanced_dataset(enhanced_df):
            print("\n✅ Dataset validation passed!")
        else:
            print("\n⚠️  Dataset validation had warnings/errors")
        
        # Create sample analysis
        create_sample_analysis(enhanced_df, output_dir)
        
        # Final summary
        print(f"\n🎉 SUCCESS!")
        print("=" * 60)
        print(f"✅ Enhanced dataset created: {os.path.basename(output_path)}")
        print(f"✅ Original data preserved, UUIDs added as first column")
        print(f"✅ {len(enhanced_df)} samples now have unique identifiers")
        
        print(f"\n💡 ADVANTAGES OF UUID IMPLEMENTATION:")
        print(f"   🔍 Better tracking in distributed processing")
        print(f"   📊 Robust data lineage and audit trails")
        print(f"   🔄 Enables safe resumption and error recovery")
        print(f"   🔗 Facilitates data merging and analysis")
        print(f"   🐛 Improved debugging and reproducibility")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Update pilot study script to use mini_test_with_ids.csv")
        print(f"   2. Results will now include sample_id for better tracking")
        print(f"   3. Analysis will be more robust with unique identifiers")
        
        # Show sample of the enhanced data
        print(f"\n📖 SAMPLE OF ENHANCED DATA:")
        print("=" * 60)
        sample_cols = ['sample_id', 'kbli_code', 'category']
        if len(enhanced_df) > 0:
            print(enhanced_df[sample_cols].head(3).to_string(index=False))
        
    except Exception as e:
        print(f"\n❌ Error adding UUIDs to dataset: {str(e)}")
        raise

if __name__ == "__main__":
    main()
