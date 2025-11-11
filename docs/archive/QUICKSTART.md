# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add Your Data Files

Copy your XLSX and CSV files to:
- Excel files → `raw_data/xlsx/`
- CSV files → `raw_data/csv/`

### 3. Run AI Analysis

```bash
python ai_data_analyzer.py
```

This generates comprehensive reports in `analysis/ai_responses/` with:
- Column listings and samples
- Data quality checks
- AI prompts for further analysis

### 4. Use AI Responses

Open the generated JSON files and use the prompts with:
- ChatGPT
- Claude
- Other AI tools

They'll help you understand your data structure and create ETL pipelines.

### 5. Build ETL Pipelines

```python
from etl_scripts.base_etl import BaseETL
from pathlib import Path

etl = BaseETL()
etl.run(source_file=Path('raw_data/csv/your_file.csv'))
```

### 6. Setup GitHub (Optional)

See `SETUP_GIT.md` for detailed instructions.

Quick version:
```bash
# Create repo on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/nj-cad-dv-analysis.git
git push -u origin main
```

## 📊 Data Analysis Workflow

```
Raw Data → AI Analysis → ETL Processing → Insights
   ↓            ↓              ↓              ↓
xlsx/csv   ai_responses   processed_data   notebooks/
```

## 🔍 What Gets Analyzed

1. **Column Structure**: All columns with data types and samples
2. **Data Quality**: Missing values, outliers, format issues
3. **Demographics**: Race, gender, age, location distributions
4. **Recommendations**: AI suggests ETL strategies

## 📁 Project Structure

```
nj_cad_dv_analysis/
├── raw_data/           ← Put your data here
│   ├── xlsx/
│   └── csv/
├── analysis/           ← AI reports appear here
├── etl_scripts/        ← Your ETL code
├── processed_data/     ← Clean data output
└── notebooks/          ← Jupyter analysis
```

## 🎯 Common Tasks

### Analyze a Single File
```python
from ai_data_analyzer import DataAnalyzer

analyzer = DataAnalyzer()
result = analyzer.analyze_file('raw_data/csv/file.csv')
```

### Demographic Analysis
```python
from etl_scripts.base_etl import DemographicETL
import pandas as pd

demo = DemographicETL()
df = pd.read_csv('your_file.csv')
insights = demo.analyze_demographics(df)
print(insights)
```

### Custom ETL
```python
config = {
    'column_mappings': {'OldName': 'new_name'},
    'type_conversions': {'date': 'datetime64'},
    'filters': {'status': 'active'}
}

etl = BaseETL()
etl.run('input.xlsx', config=config)
```

## 📝 Next Steps

- [ ] Add your raw data files
- [ ] Run AI analysis
- [ ] Review generated prompts
- [ ] Build custom ETL pipelines
- [ ] Create visualizations
- [ ] Generate reports

## 💡 Tips

- Start with one small file to test
- Review AI suggestions before building ETL
- Keep raw data separate from processed data
- Use git for version control
- Log everything to track progress

## 🆘 Need Help?

- Check `README.md` for full documentation
- Review logs in `logs/analysis.log`
- See AI responses in `analysis/ai_responses/`
- Read `SETUP_GIT.md` for GitHub setup

## 📅 Data Coverage

- **Time Period**: January 2023 - October 31, 2025
- **Source**: CAD/RMS and Domestic Violence reports
- **Location**: State of New Jersey

Happy analyzing! 🎉

