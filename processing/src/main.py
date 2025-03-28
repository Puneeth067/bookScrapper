import os
import sys
import json

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Import the processor module
from processing.processor import lambdaHandler

def main():
    # Default input for processing
    inputDA = {
        "processing_input": {
            "raw_data_id": "102"  # Default raw data ID
        }
    }
    
    # Call the lambda handler
    result = lambdaHandler(inputDA, "")
    
    # Print the result
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()