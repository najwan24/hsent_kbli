"""
ACSES Pilot Study - Codebook Processing Pipeline
Handles KBLI codebook processing and hierarchical structure creation
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional

from ..utils.common import setup_logging, load_csv_with_dtype, create_timestamp, print_progress

class CodebookProcessor:
    """Handles KBLI codebook processing and hierarchical structure creation"""
    
    def __init__(self, input_path: Path, output_path: Path):
        """
        Initialize codebook processor
        
        Args:
            input_path: Path to input KBLI codebook CSV
            output_path: Path where hierarchical codebook will be saved
        """
        self.input_path = input_path
        self.output_path = output_path
        self.logger = setup_logging(f"{__name__}.CodebookProcessor")
    
    def create_lookup_dict(self, df: pd.DataFrame) -> Dict[str, Tuple[str, str]]:
        """
        Create a fast lookup dictionary for all codes.
        
        Args:
            df: DataFrame containing the codebook data
            
        Returns:
            Dictionary mapping code -> (title, description)
        """
        lookup = {}
        
        for _, row in df.iterrows():
            code = str(row['kode'])
            title = str(row['judul'])
            description = str(row['deskripsi']) if pd.notna(row['deskripsi']) else ""
            lookup[code] = (title, description)
        
        self.logger.info(f"Created lookup dictionary with {len(lookup)} entries")
        return lookup
    
    def process(self) -> bool:
        """
        Transform the codebook into a hierarchical format for easy prompt creation.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Loading KBLI codebook from {self.input_path}")
            
            # Load the CSV with proper dtype for codes
            df = load_csv_with_dtype(self.input_path, {'kode': str})
            self.logger.info(f"Loaded {len(df)} entries from codebook")
            
            # Create a fast lookup dictionary for all codes
            level_info = self.create_lookup_dict(df)
            
            # Get only the 5-digit codes to iterate over
            df_5_digit = df[df['digit'] == 5].copy()
            self.logger.info(f"Found {len(df_5_digit)} 5-digit codes to process")
            
            # Process hierarchical data
            hierarchical_data = []
            total_codes = len(df_5_digit)
            
            for idx, (_, row) in enumerate(df_5_digit.iterrows()):
                code_5 = str(row['kode'])
                code_4 = code_5[:4]  # First 4 characters
                code_3 = code_5[:3]  # First 3 characters  
                code_2 = code_5[:2]  # First 2 characters
                code_1 = str(row['kategori'])  # The 'kategori' column holds the Section letter
                
                # Build a new, flat dictionary for this 5-digit code
                entry = {
                    'code_5': code_5,
                    'title_5': level_info.get(code_5, ("", ""))[0],
                    'desc_5': level_info.get(code_5, ("", ""))[1],
                    'code_4': code_4,
                    'title_4': level_info.get(code_4, ("", ""))[0],
                    'code_3': code_3,
                    'title_3': level_info.get(code_3, ("", ""))[0],
                    'code_2': code_2,
                    'title_2': level_info.get(code_2, ("", ""))[0],
                    'code_1': code_1,
                    'title_1': level_info.get(code_1, ("", ""))[0]
                }
                
                hierarchical_data.append(entry)
                
                # Print progress every 100 entries
                if (idx + 1) % 100 == 0 or (idx + 1) == total_codes:
                    print_progress(idx + 1, total_codes, "Processing codes")
            
            # Convert the list of dictionaries to a DataFrame and save
            hierarchical_df = pd.DataFrame(hierarchical_data)
            
            # Create output directory if it doesn't exist
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to CSV
            hierarchical_df.to_csv(self.output_path, index=False)
            
            self.logger.info(f"Hierarchical codebook created successfully with {len(hierarchical_df)} entries")
            self.logger.info(f"Output saved to: {self.output_path}")
            
            # Display sample of the output
            self.logger.info("Sample of hierarchical codebook:")
            sample_df = hierarchical_df.head(3)
            for _, row in sample_df.iterrows():
                self.logger.info(f"  {row['code_5']}: {row['title_5']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing codebook: {e}")
            return False
    
    def validate_output(self) -> bool:
        """
        Validate the generated hierarchical codebook
        
        Returns:
            True if validation passes, False otherwise
        """
        try:
            if not self.output_path.exists():
                self.logger.error("Output file does not exist")
                return False
            
            # Load and validate the hierarchical codebook
            df = load_csv_with_dtype(self.output_path)
            
            required_columns = [
                'code_5', 'title_5', 'desc_5',
                'code_4', 'title_4',
                'code_3', 'title_3',
                'code_2', 'title_2',
                'code_1', 'title_1'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return False
            
            # Check for empty code columns
            for code_col in ['code_5', 'code_4', 'code_3', 'code_2', 'code_1']:
                empty_count = df[code_col].isna().sum()
                if empty_count > 0:
                    self.logger.warning(f"Found {empty_count} empty values in {code_col}")
            
            self.logger.info(f"Validation passed: {len(df)} entries with all required columns")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating output: {e}")
            return False
