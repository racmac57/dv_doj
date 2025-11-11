"""
Fix column headers in the DV state form file and convert boolean values
Also maps Case Numbers to RMS file for location data
"""

import pandas as pd
import re
from pathlib import Path
import logging

YES_NO_MAP_FILE = Path("docs/mappings/yes_no_bool_map.csv")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_boolean_vocab(path: Path = YES_NO_MAP_FILE):
    if not path.exists():
        logger.warning("Boolean mapping file %s not found. Falling back to defaults.", path)
        truthy = {"X", "O", "Y", "YES", "T", "TRUE", "1"}
        falsy = {"N", "NO", "F", "FALSE", "0", ""}
    else:
        df = pd.read_csv(path)
        truthy = {str(v).strip().upper() for v in df[df["boolean"].astype(str).str.lower() == "true"]["raw"]}
        falsy = {str(v).strip().upper() for v in df[df["boolean"].astype(str).str.lower() == "false"]["raw"]}
    return truthy, falsy

def to_pascal_case(name):
    """Convert a string to PascalCase"""
    # Remove special characters, split by spaces, underscores, or hyphens
    words = re.split(r'[\s_\-]+', name)
    # Capitalize first letter of each word and join
    return ''.join(word.capitalize() for word in words if word)

def fix_column_headers(df):
    """
    Fix column headers according to specifications:
    1. Replace "#" in column names with proper name (e.g., "Case #" -> "CaseNumber")
    2. Remove "g" prefix from columns starting with "g" (e.g., "gMunicipalityCode" -> "MunicipalityCode")
    3. Convert "Offense Date" to PascalCase
    4. Handle suffix columns (like _I, _H, _M, _W, _B) - keep but understand them
    5. Ensure all headers are in PascalCase
    """
    column_mapping = {}
    
    for col in df.columns:
        original_col = col
        new_col = col
        
        # 1. Replace "Case #" with "CaseNumber"
        if col == "Case #":
            new_col = "CaseNumber"
        
        # 2. Remove "g" prefix (convert gMunicipalityCode -> MunicipalityCode)
        elif col.startswith('g') and len(col) > 1:
            # Remove the 'g' prefix and capitalize first letter of remaining part
            new_col = col[1].upper() + col[2:]
        
        # 3. Convert "Offense Date" or similar date columns to PascalCase
        elif 'Offense' in col and 'Date' in col:
            new_col = to_pascal_case(col.replace(' ', ''))
        
        # 4. Handle columns with spaces (convert to PascalCase)
        elif ' ' in col:
            new_col = to_pascal_case(col)
        
        # 5. Convert single lowercase letters to uppercase
        elif len(col) == 1 and col.islower():
            new_col = col.upper()
        
        # 6. Ensure first letter is capitalized for columns that need it
        elif col and not col[0].isupper():
            # Already PascalCase columns with underscores should be left alone
            if '_' in col and col.split('_')[0][0].isupper():
                new_col = col  # Keep as is
            else:
                new_col = col[0].upper() + col[1:] if len(col) > 1 else col.upper()
        
        else:
            new_col = col  # Already correct
        
        if original_col != new_col:
            column_mapping[original_col] = new_col
            logger.info(f"Renaming: '{original_col}' -> '{new_col}'")
    
    # Apply renaming
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    return df, column_mapping

def convert_boolean_values(df):
    """
    Convert 'X' and uppercase 'O' values to boolean True
    Also convert 0/empty to False where appropriate
    """
    logger.info("Converting boolean values (X, O -> True)")
    
    cols_to_convert = []
    truthy_values, falsy_values = load_boolean_vocab()
    
    # First pass: identify columns that should be converted
    for col in df.columns:
        try:
            col_series = df.loc[:, col]
            if col_series.dtype == 'object':
                unique_vals = col_series.dropna().unique()
                # Convert to strings for comparison
                unique_strs = [str(v).strip().upper() for v in unique_vals]
                # If column has mostly X, O, 0, or empty, treat as boolean
                if len(unique_vals) <= 3 and any(v in unique_strs for v in ['X', 'O', '0', '']):
                    cols_to_convert.append(col)
        except Exception as e:
            logger.warning(f"Could not check column {col}: {e}")
            continue
    
    # Second pass: convert identified columns
    for col in cols_to_convert:
        logger.info(f"Converting column '{col}' to boolean")
        def _map_value(val):
            if pd.isna(val):
                return False
            normalized = str(val).strip().upper()
            if normalized in truthy_values:
                return True
            if normalized in falsy_values:
                return False
            return val

        df[col] = df[col].apply(_map_value)
    
    return df

def examine_files():
    """Examine the files to understand their structure"""
    dv_file = Path('raw_data/xlsx/_2023_2025_10_31_dv.xlsx')
    rms_file = Path('raw_data/xlsx/_2023_2025_10_31_dv_rms.xlsx')
    
    logger.info(f"Examining {dv_file}")
    df_dv = pd.read_excel(dv_file, nrows=5)
    
    logger.info(f"DV file columns ({len(df_dv.columns)}):")
    problematic_cols = []
    for col in df_dv.columns:
        issues = []
        if '#' in col:
            issues.append("contains #")
        if col.startswith('g') or col.startswith('G'):
            issues.append("starts with g")
        if col and not col[0].isupper():
            issues.append("doesn't start with uppercase")
        if issues:
            problematic_cols.append((col, issues))
            print(f"  {col:50s} - {', '.join(issues)}")
    
    logger.info(f"\nExamining {rms_file}")
    df_rms = pd.read_excel(rms_file, nrows=5)
    
    logger.info(f"RMS file columns ({len(df_rms.columns)}):")
    case_cols = [c for c in df_rms.columns if 'case' in c.lower() or 'number' in c.lower()]
    print(f"  Case number columns: {case_cols}")
    
    location_cols = [c for c in df_rms.columns if any(term in c.lower() for term in ['address', 'location', 'street', 'lat', 'lon', 'x', 'y'])]
    print(f"  Location columns: {location_cols}")
    
    return df_dv, df_rms

def process_dv_file(input_file, output_file=None):
    """
    Process the DV file to fix headers and convert boolean values
    """
    logger.info(f"Processing {input_file}")
    
    # Read the file
    df = pd.read_excel(input_file, engine='openpyxl')
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Fix column headers
    df, column_mapping = fix_column_headers(df)
    
    # Convert boolean values
    df = convert_boolean_values(df)
    
    # Save output
    if output_file is None:
        output_file = Path('processed_data') / f"{Path(input_file).stem}_fixed.xlsx"
    
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving to {output_file}")
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    logger.info(f"Processed file saved. Changed {len(column_mapping)} column names")
    
    return df, column_mapping

if __name__ == "__main__":
    # First examine the files
    print("="*80)
    print("EXAMINING FILES")
    print("="*80)
    examine_files()
    
    print("\n" + "="*80)
    print("PROCESSING DV FILE")
    print("="*80)
    
    # Process the DV file
    input_file = Path('raw_data/xlsx/_2023_2025_10_31_dv.xlsx')
    df_fixed, mapping = process_dv_file(input_file)
    
    print(f"\nFixed {len(mapping)} column names")
    print("\nColumn name changes:")
    for old, new in sorted(mapping.items()):
        print(f"  {old:50s} -> {new}")
    
    print(f"\nOutput saved to: processed_data/_2023_2025_10_31_dv_fixed.xlsx")

