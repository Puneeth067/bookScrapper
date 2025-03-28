import logging

class ProcessingConfig:
    # Maximum number of retries for processing
    MAX_RETRIES = 3
    
    # Timeout for processing operations
    PROCESSING_TIMEOUT = 30
    
    # Maximum number of rows to process (optional safety limit)
    MAX_ROWS = 10000
    
    # Logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='processing.log'
    )
    
    # Logger for processing operations
    LOGGER = logging.getLogger('BookProcessorLogger')
    
    # Output directory for processed data
    PROCESSED_DATA_DIR = 'processed_data'