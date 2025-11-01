"""
Base ETL Pipeline for CAD/RMS and Domestic Violence Data
Provides framework for extracting, transforming, and loading data
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class BaseETL:
    """Base ETL class for data processing"""
    
    def __init__(self, raw_data_dir='raw_data', output_dir='processed_data'):
        self.raw_data_dir = Path(raw_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def extract(self, source_file: Path) -> pd.DataFrame:
        """
        Extract data from source file
        
        Args:
            source_file: Path to source file
            
        Returns:
            DataFrame with raw data
        """
        self.logger.info(f"Extracting from {source_file}")
        
        try:
            if source_file.suffix.lower() == '.xlsx':
                df = pd.read_excel(source_file, engine='openpyxl')
            elif source_file.suffix.lower() == '.csv':
                df = pd.read_csv(source_file, encoding='utf-8', low_memory=False)
            else:
                raise ValueError(f"Unsupported file type: {source_file.suffix}")
            
            self.logger.info(f"Extracted {len(df)} rows")
            return df
            
        except Exception as e:
            self.logger.error(f"Error extracting {source_file}: {str(e)}")
            raise
    
    def transform(self, df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
        """
        Transform data according to specified rules
        
        Args:
            df: Raw DataFrame
            config: Transformation configuration
            
        Returns:
            Transformed DataFrame
        """
        self.logger.info("Transforming data")
        
        # Apply transformations based on config
        if config:
            # Rename columns if specified
            if 'column_mappings' in config:
                df = df.rename(columns=config['column_mappings'])
            
            # Clean data types if specified
            if 'type_conversions' in config:
                for col, dtype in config['type_conversions'].items():
                    if col in df.columns:
                        try:
                            df[col] = df[col].astype(dtype)
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Could not convert {col} to {dtype}: {e}")
            
            # Apply filters if specified
            if 'filters' in config:
                for filter_col, filter_value in config['filters'].items():
                    if filter_col in df.columns:
                        df = df[df[filter_col] == filter_value]
        
        # General cleanup
        df = self._standardize_columns(df)
        df = self._clean_values(df)
        
        return df
    
    def load(self, df: pd.DataFrame, output_file: Path, format='parquet'):
        """
        Load data to output file
        
        Args:
            df: DataFrame to load
            output_file: Output file path
            format: Output format (parquet, csv, etc.)
        """
        self.logger.info(f"Loading to {output_file}")
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'parquet':
            df.to_parquet(output_file, index=False)
        elif format == 'csv':
            df.to_csv(output_file, index=False)
        elif format == 'excel':
            df.to_excel(output_file, index=False)
        else:
            raise ValueError(f"Unsupported output format: {format}")
        
        self.logger.info(f"Loaded {len(df)} rows to {output_file}")
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names"""
        # Remove extra whitespace
        df.columns = df.columns.str.strip()
        # Convert to lowercase
        df.columns = df.columns.str.lower()
        # Replace spaces with underscores
        df.columns = df.columns.str.replace(' ', '_')
        
        return df
    
    def _clean_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean values in the DataFrame"""
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        
        return df
    
    def run(self, source_file: Path, output_file: Optional[Path] = None, 
            config: Optional[Dict] = None, output_format='parquet'):
        """
        Run complete ETL pipeline
        
        Args:
            source_file: Source file path
            output_file: Output file path (optional)
            config: ETL configuration
            output_format: Output file format
        """
        try:
            # Extract
            raw_df = self.extract(source_file)
            
            # Transform
            transformed_df = self.transform(raw_df, config)
            
            # Load
            if output_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = self.output_dir / f"{source_file.stem}_processed_{timestamp}.{output_format}"
            
            self.load(transformed_df, output_file, format=output_format)
            
            self.logger.info("ETL pipeline completed successfully")
            
            return transformed_df
            
        except Exception as e:
            self.logger.error(f"ETL pipeline failed: {str(e)}")
            raise


class DemographicETL(BaseETL):
    """Specialized ETL for demographic data analysis"""
    
    def extract_demographics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract demographic insights from data
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            DataFrame with demographic summaries
        """
        self.logger.info("Extracting demographic insights")
        
        # Common demographic columns to look for
        demo_columns = {
            'race': ['race', 'ethnicity', 'racial_category', 'race_ethnicity'],
            'gender': ['gender', 'sex', 'gender_identity'],
            'age': ['age', 'dob', 'date_of_birth', 'birth_date'],
            'location': ['county', 'city', 'municipality', 'zip_code']
        }
        
        demographic_data = {}
        
        for demo_type, possible_cols in demo_columns.items():
            found_col = None
            for col in possible_cols:
                if col in df.columns:
                    found_col = col
                    break
            
            if found_col:
                demographic_data[demo_type] = {
                    'column': found_col,
                    'values': df[found_col].value_counts().to_dict()
                }
        
        return demographic_data
    
    def analyze_demographics(self, df: pd.DataFrame) -> Dict:
        """Analyze demographic distributions"""
        demographics = self.extract_demographics(df)
        
        analysis = {
            'extraction_date': datetime.now().isoformat(),
            'demographic_fields': demographics,
            'summary_statistics': {}
        }
        
        for demo_type, data in demographics.items():
            values = data['values']
            analysis['summary_statistics'][demo_type] = {
                'unique_values': len(values),
                'total_count': sum(values.values()),
                'distribution': values
            }
        
        return analysis


def create_etl_config(file_name: str, column_mappings: Dict, 
                      type_conversions: Optional[Dict] = None,
                      filters: Optional[Dict] = None) -> Dict:
    """
    Create ETL configuration dictionary
    
    Args:
        file_name: Name of the file this config applies to
        column_mappings: Dictionary mapping old column names to new ones
        type_conversions: Dictionary of column name to data type conversions
        filters: Dictionary of filters to apply
        
    Returns:
        ETL configuration dictionary
    """
    config = {
        'source_file': file_name,
        'column_mappings': column_mappings,
        'type_conversions': type_conversions or {},
        'filters': filters or {}
    }
    
    return config


if __name__ == "__main__":
    # Example usage
    etl = BaseETL()
    
    # Example: Run ETL with configuration
    config_example = {
        'column_mappings': {
            'OldName': 'new_name',
        },
        'type_conversions': {
            'date_column': 'datetime64'
        }
    }
    
    # Uncomment when you have actual data files:
    # etl.run(
    #     source_file=Path('raw_data/csv/example_file.csv'),
    #     config=config_example
    # )

