import os
import json
import pandas as pd
import pyarrow.parquet as pq
from processing.config import ProcessingConfig

class BookProcessor:
    def __init__(self):
        self.logger = ProcessingConfig.LOGGER
        
        # Use absolute path for processed data directory
        self.processed_data_dir = os.path.join(os.path.dirname(__file__), 'processed_data')
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
        
        # Limit rows if needed
        if len(df) > ProcessingConfig.MAX_ROWS:
            self.logger.warning(f"Truncating data to {ProcessingConfig.MAX_ROWS} rows")
            df = df.head(ProcessingConfig.MAX_ROWS)
        
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
        
        ProcessingConfig.LOGGER.info(f"Received processing input: {processing_input}")
        
        # Update path to use absolute path
        config_path = os.path.join(os.path.dirname(__file__), 'run_raw_data.json')
        
        ProcessingConfig.LOGGER.info(f"Loading config from: {config_path}")
        
        # Load raw data configurations
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Find matching raw data file
        file_config = next((f for f in config['raw_data_files'] if f['id'] == file_id), None)
        
        if not file_config:
            ProcessingConfig.LOGGER.error(f"No raw data file found with ID {file_id}")
            raise ValueError(f"No raw data file found with ID {file_id}")
        
        # Get the project root directory (bookScrapper directory)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Convert relative path to absolute path, using project root
        absolute_input_path = os.path.normpath(os.path.join(project_root, file_config['path']))
        
        ProcessingConfig.LOGGER.info(f"Project root: {project_root}")
        ProcessingConfig.LOGGER.info(f"Absolute input path: {absolute_input_path}")
        ProcessingConfig.LOGGER.info(f"Found raw data file config: {file_config}")
        
        # Check if input file exists
        if not os.path.exists(absolute_input_path):
            ProcessingConfig.LOGGER.error(f"Input file does not exist: {absolute_input_path}")
            raise FileNotFoundError(f"Input file not found: {absolute_input_path}")
        
        # Process books
        processor = BookProcessor()
        parquet_path = processor.process_data(absolute_input_path)
        
        if not parquet_path:
            ProcessingConfig.LOGGER.error("Processing failed: No Parquet path returned")
        
        return {
            'statusCode': 200 if parquet_path else 500,
            'body': json.dumps({
                'message': 'Processing completed successfully' if parquet_path else 'Processing failed',
                'parquet_path': parquet_path
            })
        }
    except Exception as e:
        ProcessingConfig.LOGGER.error(f"Processing failed: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Processing failed',
                'error': str(e)
            })
        }