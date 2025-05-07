import os
import csv
import json
import logging
import requests
from bs4 import BeautifulSoup
from scrapping.config import ScrapingConfig
from urllib.parse import urljoin

class BookScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = ScrapingConfig.LOGGER
        
        # Update raw_data directory path to be within the scrapping folder
        self.raw_data_dir = os.path.join(os.path.dirname(__file__), 'raw_data')
        os.makedirs(self.raw_data_dir, exist_ok=True)
        
        self.logger.info(f"Initialized BookScraper with base URL: {base_url}")
        self.logger.info(f"Raw data directory: {self.raw_data_dir}")

    def _extract_book_details(self, book):
        """Extract details for a single book."""
        try:
            # Title
            title = book.find('h3').find('a')['title']
            
            # Price
            price = book.find('div', class_='product_price').find('p', class_='price_color').text[1:]
            
            # Rating
            rating_class = book.find('p', class_='star-rating')['class'][1]
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            rating = rating_map.get(rating_class, 0)
            
            # Availability
            availability = book.find('div', class_='product_price').find('p', class_='instock availability').text.strip()
            
            # Product URL - Fix the URL construction
            relative_url = book.find('h3').find('a')['href']
            
            # Determine if we're dealing with full or relative paths
            if relative_url.startswith('http'):
                product_url = relative_url
            else:
                # Remove '../' prefix if present for better URL joining
                cleaned_relative_url = relative_url
                if cleaned_relative_url.startswith('../'):
                    cleaned_relative_url = cleaned_relative_url[3:]
                
                # Use urljoin properly based on the current context
                if self.base_url.endswith('/catalogue/'):
                    product_url = urljoin(self.base_url, cleaned_relative_url)
                else:
                    product_url = urljoin(self.base_url, 'catalogue/' + cleaned_relative_url)
            
            # Get subcategory from the book detail page
            subcategory = "Unknown"  # Default value
            try:
                # Add more robust request handling with retries
                retries = 0
                while retries < ScrapingConfig.MAX_RETRIES:
                    try:
                        self.logger.info(f"Fetching detail page for '{title}': {product_url}")
                        detail_page = requests.get(product_url, timeout=ScrapingConfig.REQUEST_TIMEOUT)
                        detail_page.raise_for_status()
                        
                        detail_soup = BeautifulSoup(detail_page.text, 'html.parser')
                        
                        # Try multiple strategies to get the category
                        # Strategy 1: Via breadcrumb
                        breadcrumb = detail_soup.find('ul', class_='breadcrumb')
                        if breadcrumb and len(breadcrumb.find_all('li')) >= 3:
                            subcategory_element = breadcrumb.find_all('li')[2]
                            subcategory = subcategory_element.text.strip()
                        
                        # Strategy 2: Via UL navigation if breadcrumb failed
                        if subcategory == "Unknown":
                            category_nav = detail_soup.select('ul.nav-list > li > ul > li > a')
                            if category_nav:
                                current_category = detail_soup.select('ul.nav-list > li > ul > li.active > a')
                                if current_category:
                                    subcategory = current_category[0].text.strip()
                        
                        # If we found a subcategory, break out of retry loop
                        if subcategory != "Unknown":
                            break
                        
                        retries += 1
                        
                    except requests.RequestException as e:
                        self.logger.warning(f"Request failed for {title} (attempt {retries+1}): {e}")
                        retries += 1
                        if retries >= ScrapingConfig.MAX_RETRIES:
                            raise
                        
                if subcategory == "Unknown":
                    self.logger.warning(f"Could not determine subcategory for '{title}' after {ScrapingConfig.MAX_RETRIES} attempts")
                    
            except Exception as e:
                self.logger.warning(f"Failed to get subcategory for '{title}': {e}")
            
            return {
                'Title': title,
                'Price': price,
                'Rating': rating,
                'Availability': availability,
                'URL': product_url,
                'Subcategory': subcategory
            }
        except Exception as e:
            self.logger.error(f"Error extracting book details: {e}")
            return None
    
    def scrape_books(self):
        """Scrape books from all pages."""
        books_data = []
        
        try:
            page_url = self.base_url
            page_count = 0
            
            while page_url and page_count < ScrapingConfig.MAX_PAGES:
                self.logger.info(f"Scraping page: {page_url}")
                
                # Fetch the page
                try:
                    response = requests.get(page_url, timeout=ScrapingConfig.REQUEST_TIMEOUT)
                    response.raise_for_status()
                except requests.RequestException as e:
                    self.logger.error(f"HTTP request error for {page_url}: {e}")
                    break
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                books = soup.find_all('article', class_='product_pod')
                
                self.logger.info(f"Found {len(books)} books on this page")
                
                # Extract book details
                for book in books:
                    book_details = self._extract_book_details(book)
                    if book_details:
                        books_data.append(book_details)
                
                # Check for next page
                next_link = soup.find('li', class_='next')
                if next_link:
                    # Construct the next page URL correctly
                    next_page_link = next_link.find('a')['href']
                    page_url = urljoin(page_url, next_page_link)
                    page_count += 1
                else:
                    page_url = None
        
        except Exception as e:
            self.logger.error(f"Unexpected error during scraping: {e}")
            return None
        
        # Save to CSV
        csv_path = os.path.join(self.raw_data_dir, 'books_data.csv')
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                if books_data:
                    fieldnames = books_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(books_data)
            
            self.logger.info(f"Scraped {len(books_data)} books to {csv_path}")
            return csv_path
        except Exception as e:
            self.logger.error(f"Error writing CSV: {e}")
            return None

def lambdaHandler(event, context):
    """Handler for scraping based on scraper ID."""
    try:
        scraper_input = event.get('scraper_input', {})
        scraper_id = scraper_input.get('run_scraper_id')
        
        ScrapingConfig.LOGGER.info(f"Received scraper input: {scraper_input}")
        
        # Update path to use absolute path
        config_path = os.path.join(os.path.dirname(__file__), 'run_scrapper.json')
        
        ScrapingConfig.LOGGER.info(f"Loading config from: {config_path}")
        
        # Load scraper configurations
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Find matching scraper
        scraper_config = next((s for s in config['scrapers'] if s['id'] == scraper_id), None)
        
        if not scraper_config:
            ScrapingConfig.LOGGER.error(f"No scraper found with ID {scraper_id}")
            raise ValueError(f"No scraper found with ID {scraper_id}")
        
        ScrapingConfig.LOGGER.info(f"Found scraper config: {scraper_config}")
        
        # Scrape books
        scraper = BookScraper(scraper_config['url'])
        csv_path = scraper.scrape_books()
        
        if not csv_path:
            ScrapingConfig.LOGGER.error("Scraping failed: No CSV path returned")
        
        return {
            'statusCode': 200 if csv_path else 500,
            'body': json.dumps({
                'message': 'Scraping completed successfully' if csv_path else 'Scraping failed',
                'csv_path': csv_path
            })
        }
    except Exception as e:
        ScrapingConfig.LOGGER.error(f"Scraping failed: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Scraping failed',
                'error': str(e)
            })
        }