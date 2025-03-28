import os
import sys
import pytest
import csv
import json

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from scrapping.scrapper import lambdaHandler

class TestBookScraping:
    @pytest.fixture
    def scraper_input(self):
        return {
            "scraper_input": {
                "run_scraper_id": "102"  
            }
        }

    def test_csv_file_download(self, scraper_input):
        """Test Case 1: Verify CSV File Download"""
        result = lambdaHandler(scraper_input, "")
        assert result['statusCode'] == 200, "Scraping failed"
        
        body = json.loads(result['body'])
        csv_path = body['csv_path']
        assert os.path.exists(csv_path), "CSV file was not created"

    def test_csv_file_extraction(self, scraper_input):
        """Test Case 2: Verify CSV File Extraction"""
        result = lambdaHandler(scraper_input, "")
        body = json.loads(result['body'])
        csv_path = body['csv_path']
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            assert len(rows) > 1, "CSV file is empty"

    def test_file_type_and_format(self, scraper_input):
        """Test Case 3: Validate File Type and Format"""
        result = lambdaHandler(scraper_input, "")
        body = json.loads(result['body'])
        csv_path = body['csv_path']
        
        assert csv_path.endswith('.csv'), "File is not a CSV"
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            expected_headers = ['Title', 'Price', 'Rating', 'Availability', 'URL']
            assert headers == expected_headers, "CSV headers are incorrect"

    def test_data_structure(self, scraper_input):
        """Test Case 4: Validate Data Structure"""
        result = lambdaHandler(scraper_input, "")
        body = json.loads(result['body'])
        csv_path = body['csv_path']
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                assert all([
                    row['Title'], 
                    row['Price'], 
                    row['Rating'], 
                    row['Availability'], 
                    row['URL']
                ]), "Some required fields are missing"