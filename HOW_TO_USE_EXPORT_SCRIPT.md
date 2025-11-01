# How to Use the Excel to CSV Export Script

## Overview

The `export_excel_sheets_to_csv.py` script is **portable** and can be run from any directory without editing the code.

## Quick Start

### Method 1: Run from the Script Location

1. **Navigate to the directory with your Excel files**
   ```bash
   cd C:\path\to\your\excel\files
   ```

2. **Run the script** (adjust path to where the script is located)
   ```bash
   python "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\dv_doj\etl_scripts\export_excel_sheets_to_csv.py"
   ```

This will:
- Find ALL `.xlsx` and `.xls` files in the current directory
- Convert each to CSV
- Save CSVs in a new `output` folder in the current directory

### Method 2: Copy Script to Your Directory (Recommended)

1. **Copy the script** to the folder with your Excel files:
   ```bash
   copy "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\dv_doj\etl_scripts\export_excel_sheets_to_csv.py" "C:\path\to\your\excel\files\"
   ```

2. **Navigate to that directory**
   ```bash
   cd C:\path\to\your\excel\files
   ```

3. **Run the script**
   ```bash
   python export_excel_sheets_to_csv.py
   ```

## Command-Line Options

### Basic Usage
```bash
python export_excel_sheets_to_csv.py
```

### Convert Specific File
```bash
python export_excel_sheets_to_csv.py --xlsx myfile.xlsx
```

### Specify Output Directory
```bash
python export_excel_sheets_to_csv.py --output-dir "my_csvs"
```

### Custom Date/Time Formats
```bash
python export_excel_sheets_to_csv.py --date-format "%m/%d/%Y" --time-format "%I:%M %p"
```

### Filter Sheets by Name
```bash
# Only include sheets with "Summary" or "Report" in the name
python export_excel_sheets_to_csv.py --include Summary Report

# Exclude sheets with "Archive" or "Backup" in the name
python export_excel_sheets_to_csv.py --exclude Archive Backup
```

### Use OpenPyXL Engine (for very large files)
```bash
python export_excel_sheets_to_csv.py --engine openpyxl
```

### Disable BOM (if you don't need UTF-8 signature)
```bash
python export_excel_sheets_to_csv.py --no-bom
```

## Full Options List

```
Options:
  --xlsx FILE             Path to specific Excel file (optional, processes all if omitted)
  --output-dir DIR        Output directory for CSV files (default: 'output')
  --encoding ENCODING     Character encoding (default: 'utf-8')
  --no-bom                Disable BOM (don't use UTF-8 signature)
  --visible-only          Export only visible rows and columns
  --all-sheets            Export all sheets (default: True)
  --include-empty         Include empty sheets in export
  --include PATTERN       Include only sheets matching pattern(s)
  --exclude PATTERN       Exclude sheets matching pattern(s)
  --date-format FORMAT    Date format string (default: '%Y-%m-%d')
  --datetime-format FORMAT DateTime format string (default: '%Y-%m-%d %H:%M:%S')
  --time-format FORMAT    Time format string (default: '%H:%M:%S')
  --engine ENGINE         Engine: auto, calamine, or openpyxl (default: auto)
  --log-file FILE         Log file path (default: 'export_log.json')
```

## Examples

### Example 1: Convert All Excel Files in Current Folder
```bash
cd C:\MyData
python export_excel_sheets_to_csv.py
```
**Result**: Creates `C:\MyData\output\` with all converted CSVs

### Example 2: Convert Single File with Custom Output
```bash
python export_excel_sheets_to_csv.py --xlsx report.xlsx --output-dir reports_csv
```
**Result**: Creates `reports_csv` folder with the converted CSV

### Example 3: Convert Only Summary Sheets
```bash
python export_excel_sheets_to_csv.py --include Summary
```
**Result**: Only exports sheets with "Summary" in the name

### Example 4: Convert with Different Date Format
```bash
python export_excel_sheets_to_csv.py --date-format "%d/%m/%Y"
```
**Result**: Dates formatted as DD/MM/YYYY instead of YYYY-MM-DD

### Example 5: Process Large Files with OpenPyXL
```bash
python export_excel_sheets_to_csv.py --engine openpyxl --chunksize 1000
```
**Result**: Uses OpenPyXL engine with chunking for very large files

## Output Structure

After running, you'll get:

```
your_directory/
├── file1.xlsx              # Original Excel files
├── file2.xlsx
├── output/                 # New folder created by script
│   ├── file1.csv          # Converted CSV files
│   ├── file2.csv
│   ├── conversion_summary.json  # Summary of conversion
├── export_log.json        # Detailed log file
└── export_excel_sheets_to_csv.py  # The script (if copied here)
```

## Understanding the Output

### CSV Files
- One CSV per Excel file (if the file has one sheet)
- Or one CSV per sheet (if the file has multiple sheets)
- Named after the sheet name or filename

### conversion_summary.json
Contains:
- Start/end time
- Files processed
- Success/failure counts
- Duration
- Details for each file

### export_log.json
Detailed log with timestamps and any errors encountered

## Features

✅ **Automatic**: Finds all Excel files in current directory  
✅ **Fast**: Uses calamine engine by default (very fast)  
✅ **Smart**: Auto-selects best engine based on file size  
✅ **Flexible**: Many options for customization  
✅ **Robust**: Handles errors gracefully  
✅ **Logged**: Detailed logs and summaries  
✅ **Portable**: No code editing needed  

## Tips

1. **Keep originals**: Script never modifies Excel files
2. **Check logs**: If something fails, check `export_log.json`
3. **Start small**: Test with one file first
4. **Large files**: Use `--engine openpyxl` for 100MB+ files
5. **Multiple sheets**: Each sheet becomes a separate CSV unless you use `--xlsx`

## Troubleshooting

### "No Excel files found"
- Make sure you're in the right directory
- Check that files are `.xlsx` or `.xls` format
- Try specifying `--xlsx filename.xlsx` explicitly

### "Memory error"
- Use `--engine openpyxl` for very large files
- Or reduce `--chunksize`

### "Permission denied"
- Close any Excel files you're trying to convert
- Check file isn't read-only

### "Module not found"
- Install dependencies: `pip install -r requirements.txt`
- Key packages: pandas, openpyxl, calamine

## Current Project Usage

For this NJ CAD/DV project:

**Script location**: `etl_scripts/export_excel_sheets_to_csv.py`

**Data location**: `raw_data/xlsx/`

**To convert existing files**:
```bash
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\dv_doj\raw_data\xlsx"
python ..\..\etl_scripts\export_excel_sheets_to_csv.py
```

**Or copy the script** to `raw_data/xlsx/` and run:
```bash
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\dv_doj\raw_data\xlsx"
copy ..\..\etl_scripts\export_excel_sheets_to_csv.py .
python export_excel_sheets_to_csv.py
```

## Need Help?

Check:
- `export_log.json` for detailed logs
- `output/conversion_summary.json` for summary
- Run with verbose logging if available

