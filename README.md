# NJ CAD/RMS and Domestic Violence Data Analysis Project

## Project Overview

This project analyzes CAD/RMS and domestic violence data reported to the State of New Jersey from January 2023 to October 31, 2025. The project includes data quality analysis, ETL pipelines, and demographic insights.

## Project Structure

```
├── raw_data/
│   ├── xlsx/                 # Raw Excel files
│   └── csv/                  # Raw CSV files
├── analysis/
│   └── ai_responses/         # AI analysis outputs and prompts
├── etl_scripts/              # ETL pipeline scripts
│   └── base_etl.py          # Base ETL framework
├── src/
│   └── config/              # Configuration files
├── logs/                    # Application logs
├── notebooks/               # Jupyter notebooks for exploration
├── processed_data/          # Cleaned and transformed data (auto-created)
├── ai_data_analyzer.py      # Main AI analysis script
├── git_automation.py        # Git and GitHub automation
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git installed
- GitHub account (for remote repository)

### Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure GitHub credentials (optional, for automated commits):

Create a `.env` file in the project root:
```
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_username
GITHUB_REPO=nj-cad-dv-analysis
```

## Usage

### Step 1: Add Your Raw Data Files

Place your raw data files in the appropriate directories:
- Excel files (`.xlsx`) → `raw_data/xlsx/`
- CSV files (`.csv`) → `raw_data/csv/`

### Step 2: Run AI Data Analysis

The `ai_data_analyzer.py` script will:
1. Read all Excel and CSV files in the raw data directories
2. Generate comprehensive analysis for each file including:
   - Column listings with sample data
   - Multiple random samples for validation
   - Data quality checks (missing values, format issues, outliers)

Run the analysis:

```bash
python ai_data_analyzer.py
```

Results will be saved to `analysis/ai_responses/` as JSON files containing:
- Full analysis reports
- AI prompts for further analysis
- Data quality metrics

### Step 3: Use AI Responses

The generated prompts can be used with AI tools (like ChatGPT, Claude, etc.) to:
1. Understand the data structure and purpose of each column
2. Identify data quality issues
3. Get recommendations for ETL pipeline development
4. Generate demographic insights

### Step 4: Build ETL Pipelines

Use the base ETL framework to create custom transformation scripts:

```python
from etl_scripts.base_etl import BaseETL
from pathlib import Path

# Initialize ETL
etl = BaseETL()

# Create configuration
config = {
    'column_mappings': {
        'Old Column Name': 'new_column_name'
    },
    'type_conversions': {
        'date_column': 'datetime64'
    }
}

# Run ETL
etl.run(
    source_file=Path('raw_data/csv/your_file.csv'),
    config=config
)
```

### Step 5: Generate Demographic Insights

For demographic analysis:

```python
from etl_scripts.base_etl import DemographicETL

demo_etl = DemographicETL()
df = pd.read_parquet('processed_data/your_file.parquet')
demographics = demo_etl.analyze_demographics(df)
```

## Git and GitHub Integration

### Initial Setup

1. **Initialize Git Repository** (if not already done):
```bash
python git_automation.py --init
```

2. **Create GitHub Repository** (first time only):
```bash
python git_automation.py --create-repo
```

### Automated Git Workflows

The `git_automation.py` script provides automation for common Git/GitHub tasks:

#### Commit and Push Changes
```bash
python git_automation.py --commit-push "Your commit message"
```

#### Create a Tagged Release
```bash
python git_automation.py --tag-release v1.0.0 "Release description"
```

#### View Repository Status
```bash
python git_automation.py --status
```

#### Sync with Remote
```bash
python git_automation.py --sync
```

### Manual Git Commands

If you prefer manual control:

```bash
# Initialize repository (if not done already)
git init

# Add files
git add .

# Commit changes
git commit -m "Initial project setup"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/nj-cad-dv-analysis.git

# Push to GitHub
git push -u origin main
```

## Data Analysis Questions

The AI analysis addresses three key questions:

### 1. Column Listing and Samples
- Lists all columns in each spreadsheet
- Shows sample data from each column
- Identifies data types and unique value counts

### 2. Random Sampling
- Provides 5 additional random samples per column
- Validates data format consistency
- Identifies patterns and potential issues

### 3. Data Quality Assessment
For each column, checks:
- **Missing Values**: Counts and percentages of null/empty values
- **Format Issues**: Unexpected data types or inconsistent formats
- **Outliers**: Statistical outliers in numeric columns
- **Suspicious Values**: Placeholder values or potential errors

## Output Files

### Analysis Reports
- `{filename}_analysis_{timestamp}.json`: Full data analysis
- `{filename}_prompts_{timestamp}.json`: AI prompts for further analysis

### Processed Data
- Cleaned and standardized data in Parquet or CSV format
- Standardized column names (lowercase, underscores)
- Type-corrected data

## Logs

All operations are logged to:
- `logs/analysis.log`: Analysis and ETL operations

## GitHub Repository

**IMPORTANT**: You need to create a GitHub repository first. Options:

1. **Using the automation script** (requires GitHub token):
   ```bash
   python git_automation.py --create-repo
   ```

2. **Manually via GitHub website**:
   - Go to https://github.com/new
   - Create a new repository named `nj-cad-dv-analysis`
   - Copy the repository URL
   - Add it as remote: `git remote add origin https://github.com/YOUR_USERNAME/nj-cad-dv-analysis.git`

## Next Steps

1. Review AI analysis outputs in `analysis/ai_responses/`
2. Use AI prompts to get detailed column descriptions and recommendations
3. Create custom ETL scripts based on AI recommendations
4. Build demographic dashboards and reports
5. Conduct statistical analysis on patterns and trends

## Notes

- All file paths use forward slashes for cross-platform compatibility
- Date range: January 2023 - October 31, 2025
- Data sources: CAD/RMS and Domestic Violence reporting systems
- Geographic scope: State of New Jersey

## Support

For questions or issues with the data analysis, check:
- Logs in `logs/analysis.log`
- Analysis results in `analysis/ai_responses/`
- Data quality reports for specific issues

