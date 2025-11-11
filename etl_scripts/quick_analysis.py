"""
Quick Analysis Script for NJ CAD/DV Data
Run this script to get immediate insights from your data
"""

import json
from pathlib import Path

import pandas as pd

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def analyze_cad_data():
    """Analyze the CAD dataset"""
    print_section("NJ CAD Domestic Violence Data Analysis")
    
    # Load data
    csv_path = Path('raw_data/csv/_2023_2025_10_31_dv_cad.csv')
    
    if not csv_path.exists():
        print(f"Error: Could not find {csv_path}")
        return None
    
    print(f"Loading data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path, engine="pyarrow")
    except (ImportError, ValueError):
        df = pd.read_csv(csv_path, low_memory=False)
    print(f"Loaded {len(df):,} records with {len(df.columns)} columns")
    
    # Basic Statistics
    print_section("BASIC STATISTICS")
    print(f"Total Records: {len(df):,}")
    print(f"Date Range: {df['cYear'].min()} - {df['cYear'].max()}")
    print(f"Unique Incident Types: {df['Incident'].nunique()}")
    print(f"Unique Officers: {df['Officer'].nunique()}")
    print(f"Unique Addresses: {df['FullAddress2'].nunique()}")
    print(f"Police Zones: {df['PDZone'].nunique()}")
    
    # Incident Analysis
    print_section("TOP 15 INCIDENT TYPES")
    top_incidents = df['Incident'].value_counts().head(15)
    for incident, count in top_incidents.items():
        pct = (count / len(df)) * 100
        print(f"  {incident:.<60} {count:>6,} ({pct:>5.1f}%)")
    
    # Time Analysis
    print_section("INCIDENTS BY DAY OF WEEK")
    day_counts = df['DayofWeek'].value_counts()
    day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    for day in day_order:
        if day in day_counts.index:
            count = day_counts[day]
            pct = (count / len(df)) * 100
            print(f"  {day:.<20} {count:>6,} ({pct:>5.1f}%)")
    
    # Monthly Analysis
    print_section("INCIDENTS BY MONTH")
    month_counts = df['cMonth'].value_counts()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    for month in month_order:
        if month in month_counts.index:
            count = month_counts[month]
            print(f"  {month:.<20} {count:>6,}")
    
    # Geographic Analysis
    print_section("TOP 10 INCIDENT LOCATIONS")
    top_locations = df['FullAddress2'].value_counts().head(10)
    for location, count in top_locations.items():
        print(f"  {location[:70]:.<70} {count:>4}")
    
    # Police Zone Analysis
    print_section("INCIDENTS BY POLICE ZONE")
    zone_counts = df['PDZone'].value_counts().sort_index()
    for zone, count in zone_counts.items():
        pct = (count / len(df)) * 100
        print(f"  Zone {zone}: {count:>6,} ({pct:>5.1f}%)")
    
    # Officer Activity
    print_section("TOP 10 MOST ACTIVE OFFICERS")
    officer_counts = df['Officer'].value_counts().head(10)
    for officer, count in officer_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {officer:.<60} {count:>4} ({pct:>5.1f}%)")
    
    # Response Type Analysis
    print_section("INCIDENTS BY RESPONSE TYPE")
    response_counts = df['Response Type'].value_counts()
    for response_type, count in response_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {response_type:.<20} {count:>6,} ({pct:>5.1f}%)")
    
    # Disposition Analysis
    print_section("TOP 10 DISPOSITIONS")
    disposition_counts = df['Disposition'].value_counts().head(10)
    for disposition, count in disposition_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {disposition:.<60} {count:>6,} ({pct:>5.1f}%)")
    
    return df

def save_summary_report(df):
    """Save a summary report to JSON"""
    if df is None:
        return
    
    print_section("SAVING SUMMARY REPORT")
    
    summary = {
        'total_records': int(len(df)),
        'date_range': f"{df['cYear'].min()}-{df['cYear'].max()}",
        'total_incident_types': int(df['Incident'].nunique()),
        'total_officers': int(df['Officer'].nunique()),
        'total_addresses': int(df['FullAddress2'].nunique()),
        'total_zones': int(df['PDZone'].nunique()),
        'incidents': df['Incident'].value_counts().head(20).to_dict(),
        'officers': df['Officer'].value_counts().head(20).to_dict(),
        'locations': df['FullAddress2'].value_counts().head(20).to_dict(),
        'by_day': df['DayofWeek'].value_counts().to_dict(),
        'by_month': df['cMonth'].value_counts().to_dict(),
        'by_zone': df['PDZone'].value_counts().to_dict(),
        'by_response_type': df['Response Type'].value_counts().to_dict(),
        'dispositions': df['Disposition'].value_counts().head(20).to_dict()
    }
    
    output_file = Path('summary_report.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"Summary report saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size:,} bytes")

def main():
    """Main execution"""
    print("\n" + "#"*80)
    print("#" + " " * 20 + "NJ CAD/DV Data Quick Analysis" + " " * 26 + "#")
    print("#"*80)
    
    try:
        # Analyze CAD data
        df = analyze_cad_data()
        
        # Save summary report
        save_summary_report(df)
        
        # Final message
        print_section("ANALYSIS COMPLETE")
        print("\nNext Steps:")
        print("  1. Review the summary above")
        print("  2. Check summary_report.json for detailed results")
        print("  3. Use AI prompts in analysis/ai_responses/ for deeper insights")
        print("  4. See NEXT_STEPS.md for advanced analysis options")
        print("\nFor more help, see:")
        print("  - NEXT_STEPS.md - Detailed guide")
        print("  - ANALYSIS_SUMMARY.md - What was analyzed")
        print("  - QUICKSTART.md - Quick reference")
        
    except FileNotFoundError as e:
        print(f"\nError: Could not find data file")
        print(f"Make sure you've run: python export_excel_sheets_to_csv.py")
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        print("Check that all required packages are installed:")
        print("  pip install pandas")

if __name__ == "__main__":
    main()

