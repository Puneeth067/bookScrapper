import logging

class ScrapingConfig:
    # Maximum number of retries for HTTP requests
    MAX_RETRIES = 3
    
    # Timeout for HTTP requests in seconds
    REQUEST_TIMEOUT = 10
    
    # Maximum number of pages to scrape (to prevent infinite scraping)
    MAX_PAGES = 50
    
    # Logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='scraping.log'
    )
    
    # Logger for scraping operations
    LOGGER = logging.getLogger('BookScraperLogger')