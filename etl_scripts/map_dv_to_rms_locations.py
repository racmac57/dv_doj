"""
Map Case Numbers from DV file to RMS file to get location data
Prepares data for ArcGIS Pro mapping using arcpy
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_files(dv_file: Path, rms_file: Path):
    """Load both DV and RMS files"""
    logger.info(f"Loading DV file: {dv_file}")
    df_dv = pd.read_excel(dv_file, engine='openpyxl')
    logger.info(f"DV file: {len(df_dv)} rows, {len(df_dv.columns)} columns")
    
    logger.info(f"Loading RMS file: {rms_file}")
    df_rms = pd.read_excel(rms_file, engine='openpyxl')
    logger.info(f"RMS file: {len(df_rms)} rows, {len(df_rms.columns)} columns")
    
    return df_dv, df_rms

def map_case_numbers(df_dv: pd.DataFrame, df_rms: pd.DataFrame, 
                     dv_case_col: str = 'CaseNumber',
                     rms_case_col: str = 'Case Number'):
    """
    Map Case Numbers from DV file to RMS file to get location data
    
    Args:
        df_dv: DV DataFrame
        df_rms: RMS DataFrame
        dv_case_col: Case number column name in DV file
        rms_case_col: Case number column name in RMS file
        
    Returns:
        Merged DataFrame with DV and RMS data
    """
    logger.info(f"Mapping Case Numbers: {dv_case_col} -> {rms_case_col}")
    
    # Check if columns exist
    if dv_case_col not in df_dv.columns:
        raise ValueError(f"Case number column '{dv_case_col}' not found in DV file. Available columns: {list(df_dv.columns[:10])}")
    
    if rms_case_col not in df_rms.columns:
        raise ValueError(f"Case number column '{rms_case_col}' not found in RMS file. Available columns: {list(df_rms.columns)}")
    
    # Show sample case numbers
    logger.info(f"DV Case Number sample: {df_dv[dv_case_col].head().tolist()}")
    logger.info(f"RMS Case Number sample: {df_rms[rms_case_col].head().tolist()}")
    
    # Merge on case numbers
    logger.info("Merging DV and RMS data...")
    merged_df = pd.merge(
        df_dv,
        df_rms,
        left_on=dv_case_col,
        right_on=rms_case_col,
        how='left',
        suffixes=('_DV', '_RMS')
    )
    
    logger.info(f"Merged file: {len(merged_df)} rows (from {len(df_dv)} DV rows)")
    
    # Check match rate
    matched = merged_df[rms_case_col].notna().sum()
    match_rate = (matched / len(df_dv)) * 100
    logger.info(f"Matched {matched}/{len(df_dv)} cases ({match_rate:.1f}%)")
    
    return merged_df

def prepare_for_arcgis(df: pd.DataFrame, output_file: Path):
    """
    Prepare data for ArcGIS Pro mapping
    
    Args:
        df: Merged DataFrame with location data
        output_file: Output file path
    """
    logger.info(f"Preparing data for ArcGIS Pro mapping")
    
    # Identify location columns
    location_cols = [c for c in df.columns if any(term in c.lower() for term in 
                   ['address', 'location', 'street', 'lat', 'lon', 'x', 'y', 'coordinate'])]
    
    logger.info(f"Location columns found: {location_cols}")
    
    # Save to CSV for ArcGIS Pro
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as CSV (ArcGIS Pro can import CSV easily)
    csv_output = output_file.with_suffix('.csv')
    logger.info(f"Saving to CSV: {csv_output}")
    df.to_csv(csv_output, index=False)
    
    # Also save as Excel for review
    logger.info(f"Saving to Excel: {output_file}")
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    # Create summary
    summary = {
        'total_records': len(df),
        'records_with_location': df[location_cols[0]].notna().sum() if location_cols else 0,
        'location_columns': location_cols,
        'case_number_column_dv': 'CaseNumber' if 'CaseNumber' in df.columns else None,
        'case_number_column_rms': 'Case Number' if 'Case Number' in df.columns else None,
    }
    
    logger.info("Summary:")
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")
    
    return summary

def create_arcgis_script(df: pd.DataFrame, output_script: Path):
    """
    Create an ArcGIS Pro Python script using arcpy for mapping
    
    Args:
        df: Merged DataFrame with location data
        output_script: Path to output Python script
    """
    logger.info(f"Creating ArcGIS Pro script: {output_script}")
    
    csv_file = Path('processed_data') / 'dv_with_locations.csv'
    csv_file_abs = csv_file.resolve()
    
    script_content = f'''"""
ArcGIS Pro script to map Domestic Violence incidents with locations
Generated automatically from mapped DV and RMS data
"""

import arcpy
import os
from pathlib import Path

# Set workspace
workspace = r"{str(Path('processed_data').resolve())}"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

# Input CSV file
csv_file = r"{csv_file_abs}"

# Output feature class name
output_fc = "DV_Incidents"

print("="*80)
print("Mapping Domestic Violence Incidents")
print("="*80)
print(f"Input CSV: {{csv_file}}")
print(f"Output Feature Class: {{output_fc}}")

# Step 1: Convert CSV to feature class
# First, create XY Event Layer if we have coordinates
# Or geocode addresses if we only have addresses

# Check if CSV has coordinates
print("\\nChecking for coordinate columns...")

# If CSV has address column, geocode it
address_column = "FullAddress"  # Adjust based on your data
coordinate_columns = None  # Set if you have Lat/Lon

if coordinate_columns:
    # If you have coordinates, create XY event layer
    print("Creating XY Event Layer from coordinates...")
    xy_layer = "xy_temp_layer"
    arcpy.management.XYTableToPoint(
        csv_file,
        xy_layer,
        coordinate_columns[0],  # X field
        coordinate_columns[1],  # Y field
        coordinate_system=arcpy.SpatialReference(4326)  # WGS84
    )
    output_fc = arcpy.management.CopyFeatures(xy_layer, output_fc)
    print(f"Created feature class: {{output_fc}}")
else:
    # If only addresses, need to geocode
    print("\\nAddress geocoding required...")
    print("You can:")
    print("1. Use ArcGIS Pro's Geocoding tool manually")
    print("2. Use ArcGIS Online geocoding service")
    print("3. Add the CSV to a map and use 'Display XY Data' if coordinates exist")
    print("\\nCSV file location: {{csv_file}}")

# Add additional information
print("\\n" + "="*80)
print("Next steps:")
print("1. Add the CSV file to your ArcGIS Pro map")
print("2. Right-click the table -> 'Display XY Data' to show points")
print("3. Or use 'Geocode Table' tool to geocode addresses")
print("4. Symbolize by incident type, date, or other attributes")
print("="*80)

print("\\nScript complete!")
'''
    
    output_script.parent.mkdir(parents=True, exist_ok=True)
    with open(output_script, 'w') as f:
        f.write(script_content)
    
    logger.info(f"ArcGIS script created: {output_script}")

def main():
    """Main function"""
    # File paths - use transformed file if available
    transformed_file = Path('processed_data/_2023_2025_10_31_dv_fixed_transformed.xlsx')
    fixed_file = Path('processed_data/_2023_2025_10_31_dv_fixed.xlsx')
    
    if transformed_file.exists():
        dv_file = transformed_file
        logger.info("Using transformed DV file")
    elif fixed_file.exists():
        dv_file = fixed_file
        logger.info("Using fixed DV file")
    rms_file = Path('raw_data/xlsx/_2023_2025_10_31_dv_rms.xlsx')
    
    if not dv_file.exists():
        logger.error(f"DV file not found: {dv_file}")
        logger.info("Please run fix_dv_headers.py first to create the fixed DV file")
        return
    
    if not rms_file.exists():
        logger.error(f"RMS file not found: {rms_file}")
        return
    
    # Load files
    df_dv, df_rms = load_files(dv_file, rms_file)
    
    # Show column info
    print("\n" + "="*80)
    print("FILE STRUCTURE")
    print("="*80)
    print(f"\nDV file columns ({len(df_dv.columns)}):")
    print(f"  Case number column: CaseNumber")
    print(f"  Sample case numbers: {df_dv['CaseNumber'].head(5).tolist()}")
    
    print(f"\nRMS file columns ({len(df_rms.columns)}):")
    print(f"  Columns: {list(df_rms.columns)}")
    if 'Case Number' in df_rms.columns:
        print(f"  Case Number sample: {df_rms['Case Number'].head(5).tolist()}")
    if 'FullAddress' in df_rms.columns:
        print(f"  FullAddress sample: {df_rms['FullAddress'].head(3).tolist()}")
    
    # Map case numbers
    print("\n" + "="*80)
    print("MAPPING CASE NUMBERS")
    print("="*80)
    merged_df = map_case_numbers(df_dv, df_rms)
    
    # Prepare for ArcGIS
    print("\n" + "="*80)
    print("PREPARING FOR ARCGIS PRO")
    print("="*80)
    output_file = Path('processed_data/dv_with_locations.xlsx')
    summary = prepare_for_arcgis(merged_df, output_file)
    
    # Create ArcGIS script
    arcgis_script = Path('processed_data/arcgis_map_dv_incidents.py')
    create_arcgis_script(merged_df, arcgis_script)
    
    print("\n" + "="*80)
    print("COMPLETE!")
    print("="*80)
    print(f"\nOutput files created:")
    print(f"  1. {output_file}")
    print(f"  2. {output_file.with_suffix('.csv')}")
    print(f"  3. {arcgis_script}")
    print(f"\nNext steps:")
    print(f"  1. Review the merged data in: {output_file}")
    print(f"  2. Use {arcgis_script} in ArcGIS Pro to create maps")
    print(f"  3. Or manually import the CSV into ArcGIS Pro")

if __name__ == "__main__":
    main()

