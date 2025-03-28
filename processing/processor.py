import os
import json
import pandas as pd
import pyarrow.parquet as pq
from .config import ProcessingConfig

class BookProcessor:
    def __init__(self):
        self.logger = ProcessingConfig.LOGGER
        self.processed_data_dir = ProcessingConfig.PROCESSED_DATA_DIR
        os.makedirs(self.processed_data_dir, exist_ok=True)

    def _clean_data(self, df):
        """Clean and validate the input DataFrame."""
        # Remove rows with missing critical information
        df = df.dropna(subset=['Title', 'Price', 'Rating', 'Availability', 'URL'])
        
        # Convert Price to numeric, handling potential formatting issues
        df['Price'] = pd.to_numeric(df['Price'].str.replace('£', ''), errors='coerce')
        
        # Ensure Rating is numeric and within 1-5 range
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
        df = df[(df['Rating'] >= 1) & (df['Rating'] <= 5)]
        
        # Clean Availability
        df['Availability'] = df['Availability'].apply(lambda x: 'In Stock' if 'in stock' in str(x).lower() else 'Out of Stock')
        
        return df

    def process_data(self, input_csv):
        """Process raw CSV data and save as Parquet."""
        try:
            # Read CSV
            df = pd.read_csv(input_csv)
            
            # Clean data
            df = self._clean_data(df)
            
            # Generate output Parquet filename
            output_parquet = os.path.join(self.processed_data_dir, 'books_data.parquet')
            
            # Save as Parquet
            df.to_parquet(output_parquet, index=False)
            
            self.logger.info(f"Processed {len(df)} books to {output_parquet}")
            return output_parquet
        
        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return None

def lambdaHandler(event, context):
    """Handler for processing based on file ID."""
    try:
        processing_input = event.get('processing_input', {})
        file_id = processing_input.get('raw_data_id')
        
        # Load raw data configurations
        with open(os.path.join(os.path.dirname(__file__), 'run_raw_data.json'), 'r') as f:
            config = json.load(f)
        
        # Find matching raw data file
        file_config = next((f for f in config['raw_data_files'] if f['id'] == file_id), None)
        
        if not file_config:
            raise ValueError(f"No raw data file found with ID {file_id}")
        
        # Process books
        processor = BookProcessor()
        parquet_path = processor.process_data(file_config['path'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Processing completed successfully',
                'parquet_path': parquet_path
            })
        }
    except Exception as e:
        ProcessingConfig.LOGGER.error(f"Processing failed: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Processing failed',
                'error': str(e)
            })
        }