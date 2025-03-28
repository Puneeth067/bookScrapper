import json
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor import lambdaHandler

if __name__ == "__main__":
    inputDA = {
        "processing_input": {
            "raw_data_id": "102"
        }
    }
    result = lambdaHandler(inputDA, "")
    print(json.dumps(result, indent=2))