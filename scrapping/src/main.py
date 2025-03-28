import os
import sys
import json

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Now import the scrapper module
from scrapping.scrapper import lambdaHandler

def main():
    inputDA = {
        "scraper_input": {
            "scraper_name": "data_ingestion",
            "run_scraper_id": "102"  
        }
    }
    result = lambdaHandler(inputDA, "")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()