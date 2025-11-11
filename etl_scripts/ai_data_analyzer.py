"""
AI Data Analyzer for CAD/RMS and Domestic Violence Data
Analyzes Excel and CSV files to extract metadata, column information, and data quality metrics
"""

import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path
import logging
import numpy as np

# Custom JSON encoder for numpy/pandas types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analysis.log'),
        logging.StreamHandler()
    ]
)

class DataAnalyzer:
    """Main class for analyzing raw data files"""
    
    def __init__(self, raw_data_dir='raw_data'):
        self.raw_data_dir = Path(raw_data_dir)
        self.xlsx_dir = self.raw_data_dir / 'xlsx'
        self.csv_dir = self.raw_data_dir / 'csv'
        self.results_dir = Path('analysis/ai_responses')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_file(self, file_path):
        """
        Analyze a single Excel or CSV file and generate comprehensive report
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        file_path = Path(file_path)
        logging.info(f"Analyzing file: {file_path.name}")
        
        try:
            # Read file based on extension
            if file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
            else:
                logging.error(f"Unsupported file type: {file_path.suffix}")
                return None
            
            # Perform analysis
            analysis = {
                'file_name': file_path.name,
                'analysis_date': datetime.now().isoformat(),
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': self._analyze_columns(df),
                'data_samples': self._get_data_samples(df, num_samples=5),
                'data_quality': self._check_data_quality(df)
            }
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing {file_path.name}: {str(e)}")
            return None
    
    def _analyze_columns(self, df):
        """
        Question 1: List all columns and show sample data
        
        Returns:
            Dictionary with column information
        """
        columns_info = {}
        
        for col in df.columns:
            columns_info[col] = {
                'dtype': str(df[col].dtype),
                'non_null_count': int(df[col].notna().sum()),
                'sample_values': [str(v) if pd.notna(v) else 'NULL' for v in df[col].dropna().head(10)],
                'unique_values_count': int(df[col].nunique())
            }
        
        return columns_info
    
    def _get_data_samples(self, df, num_samples=5):
        """
        Question 2: Get random samples for each column
        
        Args:
            df: DataFrame to sample from
            num_samples: Number of random samples to get
            
        Returns:
            Dictionary with random samples per column
        """
        samples = {}
        
        # Get random rows
        if len(df) > num_samples:
            random_rows = df.sample(n=min(num_samples, len(df)), random_state=42)
        else:
            random_rows = df
        
        # Extract samples for each column
        for col in df.columns:
            samples[col] = [str(v) if pd.notna(v) else 'NULL' for v in random_rows[col]]
        
        return samples
    
    def _check_data_quality(self, df):
        """
        Question 3: Run comprehensive data quality checks
        
        Args:
            df: DataFrame to check
            
        Returns:
            Dictionary with quality metrics
        """
        quality_report = {}
        
        for col in df.columns:
            quality_report[col] = {
                'missing_values': self._check_missing_values(df[col]),
                'format_issues': self._check_formats(df[col]),
                'outliers': self._check_outliers(df[col]),
                'suspicious_values': self._check_suspicious_values(df[col])
            }
        
        return quality_report
    
    def _check_missing_values(self, series):
        """Check for missing, null, or empty values"""
        total = len(series)
        null_count = series.isna().sum()
        empty_count = (series == '').sum() if series.dtype == 'object' else 0
        
        missing_total = null_count + empty_count
        missing_pct = (missing_total / total * 100) if total > 0 else 0
        
        return {
            'total_values': total,
            'null_count': int(null_count),
            'empty_string_count': int(empty_count),
            'total_missing': int(missing_total),
            'missing_percentage': round(missing_pct, 2)
        }
    
    def _check_formats(self, series):
        """Check for unexpected formats or data types"""
        issues = []
        
        # Check date format
        if series.dtype == 'object':
            sample_values = series.dropna().head(100)
            for val in sample_values:
                if isinstance(val, str):
                    # Check for inconsistent formats
                    if len(val) == 0:
                        continue
                    # Additional format checks can be added here
                    break
        
        return {
            'issues_found': issues,
            'format_consistency': 'consistent' if len(issues) == 0 else 'needs_review'
        }
    
    def _check_outliers(self, series):
        """Check for outliers in numeric columns"""
        if pd.api.types.is_numeric_dtype(series):
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            
            return {
                'has_outliers': len(outliers) > 0,
                'outlier_count': int(len(outliers)),
                'outlier_percentage': round(len(outliers) / len(series) * 100, 2) if len(series) > 0 else 0,
                'bounds': {'lower': float(lower_bound), 'upper': float(upper_bound)} if pd.notna(lower_bound) else None
            }
        else:
            return {'has_outliers': False, 'reason': 'non_numeric_column'}
    
    def _check_suspicious_values(self, series):
        """Check for suspicious or unexpected values"""
        suspicious = []
        
        if series.dtype == 'object':
            # Check for values that might be placeholders or errors
            unique_vals = series.value_counts().head(20)
            suspicious_patterns = ['N/A', 'NA', 'NULL', 'unknown', 'TBD', '#N/A', '#REF!']
            
            for pattern in suspicious_patterns:
                if pattern in series.values:
                    suspicious.append(f"Found placeholder pattern: {pattern}")
        
        return {
            'suspicious_values': suspicious,
            'requires_review': len(suspicious) > 0
        }
    
    def generate_prompts(self, analysis):
        """
        Generate AI prompts based on analysis results
        
        Returns:
            Dictionary with formatted prompts for each question
        """
        if not analysis:
            return None
        
        prompts = {
            'question_1': {
                'prompt': f"""
Analyze the following spreadsheet columns and provide sample data for each:

File: {analysis['file_name']}
Total Rows: {analysis['total_rows']}
Total Columns: {analysis['total_columns']}

Columns and Sample Data:
{json.dumps(analysis['columns'], indent=2, cls=NumpyEncoder)}

Please provide a detailed description of each column including its purpose and data type.
""",
                'analysis': analysis['columns']
            },
            'question_2': {
                'prompt': f"""
Review these additional random samples from the dataset to confirm data formats:

{json.dumps(analysis['data_samples'], indent=2, cls=NumpyEncoder)}

Are there any inconsistencies or patterns in the data structure?
""",
                'analysis': analysis['data_samples']
            },
            'question_3': {
                'prompt': f"""
Conduct a comprehensive data quality assessment:

{json.dumps(analysis['data_quality'], indent=2, cls=NumpyEncoder)}

Provide recommendations for data cleaning and ETL pipeline development.
""",
                'analysis': analysis['data_quality']
            }
        }
        
        return prompts
    
    def save_analysis(self, analysis, prompts):
        """Save analysis results and prompts to JSON files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = Path(analysis['file_name']).stem
        
        # Save full analysis
        analysis_file = self.results_dir / f"{base_name}_analysis_{timestamp}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, cls=NumpyEncoder)
        
        # Save prompts
        prompts_file = self.results_dir / f"{base_name}_prompts_{timestamp}.json"
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, indent=2, cls=NumpyEncoder)
        
        logging.info(f"Analysis saved to {analysis_file}")
        logging.info(f"Prompts saved to {prompts_file}")
        
        return analysis_file, prompts_file
    
    def run_analysis(self):
        """Run analysis on all files in raw_data directories"""
        all_files = list(self.xlsx_dir.glob('*.xlsx')) + list(self.csv_dir.glob('*.csv'))
        
        if not all_files:
            logging.warning(f"No Excel or CSV files found in {self.raw_data_dir}")
            return
        
        logging.info(f"Found {len(all_files)} files to analyze")
        
        for file_path in all_files:
            # Analyze file
            analysis = self.analyze_file(file_path)
            
            if analysis:
                # Generate prompts
                prompts = self.generate_prompts(analysis)
                
                # Save results
                self.save_analysis(analysis, prompts)
        
        logging.info("Analysis complete!")


if __name__ == "__main__":
    analyzer = DataAnalyzer()
    analyzer.run_analysis()

