import os
import sys
import pytest
import pandas as pd
import json

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor import lambdaHandler

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
        
        # Save sample data
        sample_csv_path = 'raw_data/sample_books_data.csv'
        os.makedirs('raw_data', exist_ok=True)
        sample_data.to_csv(sample_csv_path, index=False)
        
        # Update input to use sample data
        processing_input['processing_input']['raw_data_id'] = '103'
        
        # Add sample data to run_raw_data.json
        with open('processing/run_raw_data.json', 'r+') as f:
            config = json.load(f)
            config['raw_data_files'].append({
                "id": "103",
                "path": sample_csv_path
            })
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()
        
        # Process data
        result = lambdaHandler(processing_input, "")
        
        # Verify processing
        assert result['statusCode'] == 200, "Processing failed"
        
        # Verify Parquet file
        parquet_path = json.loads(result['body'])['parquet_path']
        assert os.path.exists(parquet_path), "Parquet file not created"
        
        # Read processed Parquet
        processed_df = pd.read_parquet(parquet_path)
        
        # Assertions
        assert len(processed_df) == 2, "Incorrect number of rows processed"
        assert processed_df['Rating'].max() <= 5, "Ratings not capped"
        assert processed_df['Title'].notna().all(), "Titles with missing values not removed"
        assert processed_df['Availability'].isin(['In Stock', 'Out of Stock']).all(), "Availability not standardized"