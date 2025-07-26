"""
ACSES Pilot Study - Phase 1: Codebook Preparation
This script transforms the KBLI codebook into a hierarchical format suitable for LLM prompts.
"""
##3__gold_label_curation/src/00_prepare_codebook.py
import pandas as pd
import os
from typing import Dict, Tuple, Optional

def create_lookup_from_dataframe(df: pd.DataFrame) -> Dict[str, Tuple[str, str]]:
    """
    Create a fast lookup dictionary for all codes.
    Key: code string (e.g., "01", "011", "A")
    Value: tuple of (title, description)
    """
    lookup = {}
    for _, row in df.iterrows():
        code = str(row['kode'])
        title = str(row['judul'])
        description = str(row['deskripsi']) if pd.notna(row['deskripsi']) else ""
        lookup[code] = (title, description)
    
    return lookup

def prepare_hierarchical_codebook(input_path: str, output_path: str) -> None:
    """
    Transform the codebook into a hierarchical format for easy prompt creation.
    
    Args:
        input_path: Path to the original KBLI codebook CSV
        output_path: Path where the hierarchical codebook will be saved
    """
    print("Loading KBLI codebook...")
    
    # Load the CSV with proper dtype for codes
    df = pd.read_csv(input_path, dtype={'kode': str})
    
    print(f"Loaded {len(df)} entries from codebook")
    
    # Create a fast lookup dictionary for all codes
    level_info = create_lookup_from_dataframe(df)
    print(f"Created lookup dictionary with {len(level_info)} entries")
    
    # Get only the 5-digit codes to iterate over
    df_5_digit = df[df['digit'] == 5].copy()
    print(f"Found {len(df_5_digit)} 5-digit codes")
    
    hierarchical_data = []
    
    for _, row in df_5_digit.iterrows():
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
    
    # Convert the list of dictionaries to a DataFrame and save
    hierarchical_df = pd.DataFrame(hierarchical_data)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    hierarchical_df.to_csv(output_path, index=False)
    
    print(f"Hierarchical codebook created successfully with {len(hierarchical_df)} entries")
    print(f"Output saved to: {output_path}")
    
    # Display sample of the output
    print("\nSample of hierarchical codebook:")
    print(hierarchical_df.head(3).to_string())

def main():
    """Main function to prepare the hierarchical codebook."""
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    input_path = os.path.join(project_root, "data", "input", "kbli_codebook.csv")
    output_path = os.path.join(project_root, "data", "output", "kbli_codebook_hierarchical.csv")
    
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        return
    
    try:
        prepare_hierarchical_codebook(input_path, output_path)
        print("\n✅ Codebook preparation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during codebook preparation: {str(e)}")
        raise

if __name__ == "__main__":
    main()
