import os
import sys
import pytest
import pandas as pd
import json

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from processing.processor import lambdaHandler

class TestBookProcessing:
    @pytest.fixture
    def processing_input(self):
        return {
            "processing_input": {
                "raw_data_id": "102"
            }
        }

    def test_handle_missing_invalid_data(self, processing_input):
        """Test Case 5: Handle Missing or Invalid Data"""
        # Create a sample CSV with some problematic data
        sample_data = pd.DataFrame({
            'Title': ['Book1', 'Book2', 'Book3', None],
            'Price': ['10.00', '15.50', 'invalid', '20.00'],
            'Rating': [4, 6, 3, 2],
            'Availability': ['in stock', 'out of stock', 'in stock', None],
            'URL': ['http://test1', 'http://test2', 'http://test3', 'http://test4']
        })

        # Ensure the raw_data directory exists
        os.makedirs(os.path.join(project_root, 'scrapping', 'raw_data'), exist_ok=True)

        # Save sample data
        sample_csv_path = os.path.join(project_root, 'scrapping', 'raw_data', 'sample_books_data.csv')
        sample_data.to_csv(sample_csv_path, index=False)

        # Update run_raw_data.json
        config_path = os.path.join(project_root, 'processing', 'run_raw_data.json')
        with open(config_path, 'r+') as f:
            config = json.load(f)
            config['raw_data_files'].append({
                "id": "103",
                "path": "../scrapping/raw_data/sample_books_data.csv"
            })
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()

        # Update input to use sample data
        processing_input['processing_input']['raw_data_id'] = '103'

        # Process data
        result = lambdaHandler(processing_input, "")

        # Verify processing
        assert result['statusCode'] == 200, f"Processing failed: {result.get('body')}"
        
        # Verify Parquet file
        body = json.loads(result['body'])
        parquet_path = body['parquet_path']
        assert os.path.exists(parquet_path), "Parquet file not created"
        
        # Read processed Parquet
        processed_df = pd.read_parquet(parquet_path)
        
        # Assertions
        assert len(processed_df) == 2, "Incorrect number of rows processed"
        assert processed_df['Rating'].max() <= 5, "Ratings not capped"
        assert processed_df['Title'].notna().all(), "Titles with missing values not removed"
        assert processed_df['Availability'].isin(['In Stock', 'Out of Stock']).all(), "Availability not standardized"

        # Clean up: remove the temporary CSV and update run_raw_data.json
        os.remove(sample_csv_path)
        with open(config_path, 'r+') as f:
            config = json.load(f)
            config['raw_data_files'] = [f for f in config['raw_data_files'] if f['id'] != '103']
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()