"""
Processing module for ACSES pilot study.
Handles ID generation, data enhancement, and codebook processing.
"""

import uuid
import hashlib
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime


class IDGenerator:
    """Generates unique identifiers for samples and tracking."""
    
    @staticmethod
    def generate_uuid() -> str:
        """
        Generate a UUID4 string for unique sample identification.
        
        Returns:
            UUID string
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_deterministic_id(content: str, prefix: str = "") -> str:
        """
        Generate a deterministic ID based on content hash.
        
        Args:
            content: Content to hash
            prefix: Optional prefix for the ID
            
        Returns:
            Deterministic ID string
        """
        hash_object = hashlib.md5(content.encode())
        hash_hex = hash_object.hexdigest()[:8]
        return f"{prefix}{hash_hex}" if prefix else hash_hex
    
    @staticmethod
    def generate_timestamp_id() -> str:
        """
        Generate a timestamp-based ID.
        
        Returns:
            Timestamp ID string
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]


class DataEnhancer:
    """Enhances datasets with unique IDs and metadata."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the data enhancer.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_input_dir = self.project_root / "data" / "input"
        self.data_output_dir = self.project_root / "data" / "output"
    
    def add_uuids_to_dataset(self, input_file: str, output_file: str) -> pd.DataFrame:
        """
        Add UUID identifiers to a dataset.
        
        Args:
            input_file: Input CSV filename
            output_file: Output CSV filename
            
        Returns:
            Enhanced DataFrame with UUIDs
        """
        input_path = self.data_input_dir / input_file
        output_path = self.data_input_dir / output_file
        
        # Load the dataset
        df = pd.read_csv(input_path, dtype={'kbli_code': str})
        print(f"📂 Loaded {len(df)} samples from {input_file}")
        
        # Check if sample_id already exists
        if 'sample_id' in df.columns:
            print("⚠️  sample_id column already exists. Checking for uniqueness...")
            
            if df['sample_id'].nunique() == len(df):
                print("✅ All sample_id values are unique. No changes needed.")
                return df
            else:
                print("⚠️  Duplicate sample_id values found. Regenerating UUIDs...")
                df = df.drop(columns=['sample_id'])
        
        # Generate UUIDs
        print("🔢 Generating unique UUID identifiers...")
        df['sample_id'] = [IDGenerator.generate_uuid() for _ in range(len(df))]
        
        # Verify uniqueness
        if df['sample_id'].nunique() == len(df):
            print(f"✅ Generated {len(df)} unique UUIDs")
        else:
            raise ValueError("UUID generation failed - duplicates found!")
        
        # Save enhanced dataset
        df.to_csv(output_path, index=False)
        print(f"💾 Enhanced dataset saved to {output_file}")
        
        return df
    
    def validate_enhanced_dataset(self, df: pd.DataFrame) -> bool:
        """
        Validate an enhanced dataset with UUIDs.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        print("\n🔍 VALIDATING ENHANCED DATASET")
        print("-" * 40)
        
        checks_passed = 0
        total_checks = 4
        
        # Check 1: sample_id column exists
        if 'sample_id' in df.columns:
            print("✅ sample_id column exists")
            checks_passed += 1
        else:
            print("❌ sample_id column missing")
        
        # Check 2: All sample_id values are non-null
        if df['sample_id'].notna().all():
            print("✅ All sample_id values are non-null")
            checks_passed += 1
        else:
            null_count = df['sample_id'].isna().sum()
            print(f"❌ {null_count} null sample_id values found")
        
        # Check 3: All sample_id values are unique
        if df['sample_id'].nunique() == len(df):
            print("✅ All sample_id values are unique")
            checks_passed += 1
        else:
            duplicate_count = len(df) - df['sample_id'].nunique()
            print(f"❌ {duplicate_count} duplicate sample_id values found")
        
        # Check 4: UUID format validation
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        valid_uuids = df['sample_id'].str.match(uuid_pattern, na=False).sum()
        
        if valid_uuids == len(df):
            print("✅ All sample_id values are valid UUIDs")
            checks_passed += 1
        else:
            invalid_count = len(df) - valid_uuids
            print(f"❌ {invalid_count} invalid UUID formats found")
        
        # Summary
        print(f"\n📊 Validation Summary: {checks_passed}/{total_checks} checks passed")
        
        return checks_passed == total_checks
    
    def create_sample_analysis(self, df: pd.DataFrame, output_dir: Optional[Path] = None) -> None:
        """
        Create a detailed analysis of the enhanced dataset.
        
        Args:
            df: Enhanced DataFrame to analyze
            output_dir: Directory to save analysis files
        """
        if output_dir is None:
            output_dir = self.data_output_dir
        
        # Create analysis dictionary
        analysis = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_samples": len(df),
                "columns": list(df.columns)
            },
            "uuid_stats": {
                "unique_ids": df['sample_id'].nunique(),
                "format_valid": df['sample_id'].str.match(r'^[0-9a-f-]{36}$', na=False).sum(),
                "sample_ids": df['sample_id'].head(10).tolist()
            },
            "data_distribution": {
                "kbli_codes": df['kbli_code'].value_counts().head(10).to_dict(),
                "job_desc_lengths": {
                    "min": int(df['job_description'].str.len().min()),
                    "max": int(df['job_description'].str.len().max()),
                    "mean": float(df['job_description'].str.len().mean()),
                    "median": float(df['job_description'].str.len().median())
                }
            }
        }
        
        # Save analysis
        analysis_path = output_dir / "dataset_with_ids_analysis.json"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Analysis saved to {analysis_path}")
        
        # Print summary
        print(f"\n📈 DATASET ANALYSIS SUMMARY")
        print(f"Total samples: {analysis['metadata']['total_samples']}")
        print(f"Unique UUIDs: {analysis['uuid_stats']['unique_ids']}")
        print(f"Most common KBLI codes:")
        for code, count in list(analysis['data_distribution']['kbli_codes'].items())[:5]:
            print(f"  {code}: {count} samples")


class CodebookProcessor:
    """Processes and transforms codebook data."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the codebook processor.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_input_dir = self.project_root / "data" / "input"
        self.data_output_dir = self.project_root / "data" / "output"
    
    def create_lookup_from_dataframe(self, df: pd.DataFrame) -> Dict[str, Tuple[str, str]]:
        """
        Create a fast lookup dictionary for all codes.
        
        Args:
            df: DataFrame with code information
            
        Returns:
            Dictionary mapping codes to (title, description) tuples
        """
        lookup = {}
        for _, row in df.iterrows():
            code = str(row['kode'])
            title = str(row['judul'])
            description = str(row['deskripsi']) if pd.notna(row['deskripsi']) else ""
            lookup[code] = (title, description)
        
        return lookup
    
    def prepare_hierarchical_codebook(self, input_file: str, output_file: str) -> None:
        """
        Transform the codebook into a hierarchical format for easy prompt creation.
        
        Args:
            input_file: Input KBLI codebook CSV filename
            output_file: Output hierarchical codebook CSV filename
        """
        input_path = self.data_input_dir / input_file
        output_path = self.data_output_dir / output_file
        
        print("📚 Loading KBLI codebook...")
        
        # Load the CSV with proper dtype for codes
        df = pd.read_csv(input_path, dtype={'kode': str})
        print(f"Loaded {len(df)} entries from codebook")
        
        # Create a fast lookup dictionary for all codes
        level_info = self.create_lookup_from_dataframe(df)
        print(f"Created lookup dictionary with {len(level_info)} entries")
        
        # Get only the 5-digit codes to iterate over
        df_5_digit = df[df['digit'] == 5].copy()
        print(f"Found {len(df_5_digit)} 5-digit codes")
        
        hierarchical_data = []
        
        for _, row in df_5_digit.iterrows():
            code_5 = str(row['kode'])
            
            # Extract hierarchical codes
            code_4 = code_5[:4]  # First 4 digits
            code_3 = code_5[:3]  # First 3 digits
            code_2 = code_5[:2]  # First 2 digits
            code_1 = code_5[:1]  # First 1 digit
            
            # Create hierarchical entry
            hier_entry = {
                'code_5': code_5,
                'title_5': level_info.get(code_5, ('', ''))[0],
                'desc_5': level_info.get(code_5, ('', ''))[1],
                
                'code_4': code_4,
                'title_4': level_info.get(code_4, ('', ''))[0],
                'desc_4': level_info.get(code_4, ('', ''))[1],
                
                'code_3': code_3,
                'title_3': level_info.get(code_3, ('', ''))[0],
                'desc_3': level_info.get(code_3, ('', ''))[1],
                
                'code_2': code_2,
                'title_2': level_info.get(code_2, ('', ''))[0],
                'desc_2': level_info.get(code_2, ('', ''))[1],
                
                'code_1': code_1,
                'title_1': level_info.get(code_1, ('', ''))[0],
                'desc_1': level_info.get(code_1, ('', ''))[1],
            }
            
            hierarchical_data.append(hier_entry)
        
        # Create DataFrame and save
        hierarchical_df = pd.DataFrame(hierarchical_data)
        hierarchical_df.to_csv(output_path, index=False)
        
        print(f"✅ Hierarchical codebook created with {len(hierarchical_df)} entries")
        print(f"💾 Saved to {output_file}")
        
        return hierarchical_df


# Convenience functions for backwards compatibility
def generate_unique_id() -> str:
    """Generate a UUID4 string."""
    return IDGenerator.generate_uuid()


def add_uuids_to_dataset(input_path: str, output_path: str) -> pd.DataFrame:
    """Add UUIDs to dataset - backwards compatibility function."""
    enhancer = DataEnhancer()
    return enhancer.add_uuids_to_dataset(
        Path(input_path).name, 
        Path(output_path).name
    )


def validate_enhanced_dataset(df: pd.DataFrame) -> bool:
    """Validate enhanced dataset - backwards compatibility function."""
    enhancer = DataEnhancer()
    return enhancer.validate_enhanced_dataset(df)


def create_sample_analysis(df: pd.DataFrame, output_dir: str) -> None:
    """Create sample analysis - backwards compatibility function."""
    enhancer = DataEnhancer()
    enhancer.create_sample_analysis(df, Path(output_dir))


def prepare_hierarchical_codebook(input_path: str, output_path: str) -> None:
    """Prepare hierarchical codebook - backwards compatibility function."""
    processor = CodebookProcessor()
    processor.prepare_hierarchical_codebook(
        Path(input_path).name,
        Path(output_path).name
    )
