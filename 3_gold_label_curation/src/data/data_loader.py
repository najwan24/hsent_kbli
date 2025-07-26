"""
Consolidated Data Loading Functions
Handles loading of codebooks, test datasets, and templates.
"""

import os
import pandas as pd
from typing import Optional
from pathlib import Path


class DataLoader:
    """Centralized data loading functionality."""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the data loader.
        
        Args:
            project_root: Path to project root (if None, auto-detects)
        """
        if project_root is None:
            # Auto-detect project root from current file location
            current_file = Path(__file__)
            self.project_root = current_file.parent.parent.parent
        else:
            self.project_root = Path(project_root)
    
    def load_hierarchical_codebook(self, path: Optional[str] = None) -> pd.DataFrame:
        """
        Load the hierarchical codebook CSV file.
        
        Args:
            path: Custom path to codebook (if None, uses default location)
            
        Returns:
            DataFrame with hierarchical codebook data
            
        Raises:
            FileNotFoundError: If codebook file not found
        """
        if path is None:
            path = self.project_root / "data" / "output" / "kbli_codebook_hierarchical.csv"
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Hierarchical codebook not found at {path}")
        
        df = pd.read_csv(
            path, 
            dtype={
                'code_5': str, 
                'code_4': str, 
                'code_3': str, 
                'code_2': str, 
                'code_1': str
            }
        )
        print(f"✅ Loaded hierarchical codebook with {len(df)} entries")
        return df
    
    def load_test_data(self, dataset_filename: str) -> pd.DataFrame:
        """
        Load test dataset with UUIDs (preferred) or fallback to original.
        
        Args:
            dataset_filename: Name of the dataset file
            
        Returns:
            DataFrame with test data including sample_id column
            
        Raises:
            FileNotFoundError: If neither enhanced nor original dataset found
        """
        base_path = self.project_root / "data" / "input" / dataset_filename
        enhanced_path = str(base_path).replace(".csv", "_with_ids.csv")
        
        # Try enhanced dataset with UUIDs first
        if os.path.exists(enhanced_path):
            print(f"📂 Loading enhanced dataset with UUIDs: {os.path.basename(enhanced_path)}")
            df = pd.read_csv(enhanced_path, dtype={'kbli_code': str, 'sample_id': str})
            print(f"✅ Loaded {len(df)} samples with UUID identifiers")
            
            # Verify UUID column exists
            if 'sample_id' not in df.columns:
                print("⚠️  Warning: sample_id column not found in enhanced dataset")
                df['sample_id'] = [f"row_{i}" for i in range(len(df))]
            
            return df
        
        # Fallback to original dataset
        elif os.path.exists(base_path):
            print(f"📂 Loading original dataset (no UUIDs): {os.path.basename(base_path)}")
            df = pd.read_csv(base_path, dtype={'kbli_code': str})
            print(f"✅ Loaded {len(df)} samples")
            
            # Add temporary sample_id based on row index
            df['sample_id'] = [f"row_{i}" for i in range(len(df))]
            print("⚠️  Added temporary row-based IDs (consider running 02a_add_unique_ids.py)")
            
            return df
        
        else:
            raise FileNotFoundError(f"Test data not found at {base_path} or {enhanced_path}")
    
    def load_master_template(self, path: Optional[str] = None) -> str:
        """
        Load the master prompt template.
        
        Args:
            path: Custom path to template (if None, uses default location)
            
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template file not found
        """
        if path is None:
            path = self.project_root / "prompts" / "master_prompt.txt"
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Master template not found at {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        print("✅ Loaded master prompt template")
        return template
    
    def get_codebook_entry(self, codebook: pd.DataFrame, code: str) -> Optional[pd.Series]:
        """
        Get a specific entry from the hierarchical codebook.
        
        Args:
            codebook: The hierarchical codebook DataFrame
            code: The 5-digit KBLI code to find
            
        Returns:
            Series with the codebook entry, or None if not found
        """
        matching_rows = codebook[codebook['code_5'] == str(code)]
        
        if matching_rows.empty:
            return None
        
        return matching_rows.iloc[0]


# Convenience functions for backward compatibility
def load_hierarchical_codebook(path: str) -> pd.DataFrame:
    """Load hierarchical codebook from specified path."""
    loader = DataLoader()
    return loader.load_hierarchical_codebook(path)

def load_test_data(path: str) -> pd.DataFrame:
    """Load test data from specified path."""
    loader = DataLoader()
    dataset_filename = os.path.basename(path)
    return loader.load_test_data(dataset_filename)

def load_master_template(path: str) -> str:
    """Load master template from specified path."""
    loader = DataLoader()
    return loader.load_master_template(path)
