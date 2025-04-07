# Book Scraper

## Overview

This project extracts book data from online bookstores (primarily books.toscrape.com), processes the information, and stores it in a structured Parquet file format. The pipeline consists of two main phases:

1. **Scraping Phase**: Extracts raw book data from websites and saves it as CSV
2. **Processing Phase**: Transforms, validates, and standardizes the data before storing it as Parquet files

## Project Structure

```
book-scraper/
├── scrapping/                # Data extraction module
│   ├── raw_data/             # Storage for scraped CSV files
│   ├── src/                  # Source code for scraping execution
│   ├── config.py             # Scraping configuration
│   ├── run_scrapper.json     # Scraper definitions
│   └── scrapper.py           # Core scraping logic
├── processing/               # Data transformation module
│   ├── processed_data/       # Storage for processed Parquet files
│   ├── src/                  # Source code for processing execution
│   ├── config.py             # Processing configuration
│   ├── run_raw_data.json     # Raw data definitions
│   └── processor.py          # Core processing logic
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Setup

### Set Environment

```bash
python -m venv env
# On Windows
env\Scripts\activate
# On Unix/Mac
source env/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Run Scraper

Fetches book data from the configured website and saves as CSV:

```bash
python -m scrapping.src.main
```

### Run Processor

Processes the raw CSV data and converts to Parquet format:

```bash
python -m processing.src.main
```

### Run Tests

```bash
# Test scraping functionality
pytest scrapping/src/test.py

# Test processing functionality
pytest processing/src/test.py
```

## Technical Details

### Scraping Module

The scraping module extracts the following information from each book:
- Title
- Price (with currency symbol removed)
- Rating (converted to numeric 1-5 scale)
- Availability status
- URL to book detail page

Key features:
- Pagination handling to navigate through multiple pages
- Robust error handling for network issues
- Configurable through `run_scrapper.json`

### Processing Module

The processing module performs these operations:
- Removes rows with missing critical data
- Converts price to numeric format
- Validates rating (ensuring 1-5 range)
- Standardizes availability status
- Saves as efficient Parquet format

Key features:
- Data validation and type conversion
- Handling of edge cases
- Configurable through `run_raw_data.json`

## Code Documentation

### Scraper Implementation

The `BookScraper` class handles the extraction of book data:

```python
def scrape_books(self):
    """
    Main scraping method that navigates through all book pages
    
    Returns:
        Path to saved CSV file or None if scraping fails
    """
    books_data = []
    
    try:
        page_url = self.base_url
        page_count = 0
        
        # Loop through pages until no more are found or MAX_PAGES limit reached
        while page_url and page_count < ScrapingConfig.MAX_PAGES:
            self.logger.info(f"Scraping page: {page_url}")
            
            # Fetch the page with error handling
            try:
                response = requests.get(page_url, timeout=ScrapingConfig.REQUEST_TIMEOUT)
                response.raise_for_status()
            except requests.RequestException as e:
                self.logger.error(f"HTTP request error for {page_url}: {e}")
                break
            
            # Parse HTML content and extract book data
            soup = BeautifulSoup(response.text, 'html.parser')
            books = soup.find_all('article', class_='product_pod')
            
            # Extract details for each book
            for book in books:
                book_details = self._extract_book_details(book)
                if book_details:
                    books_data.append(book_details)
            
            # Find link to next page if it exists
            next_link = soup.find('li', class_='next')
            if next_link:
                next_page_link = next_link.find('a')['href']
                page_url = urljoin(page_url, next_page_link)
                page_count += 1
            else:
                page_url = None
    
    except Exception as e:
        self.logger.error(f"Unexpected error during scraping: {e}")
        return None
    
    # Save collected data to CSV file
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
```

### Processor Implementation

The `BookProcessor` class handles data transformation:

```python
def _clean_data(self, df):
    """
    Clean and standardize the book data
    
    Args:
        df: Pandas DataFrame containing raw book data
        
    Returns:
        Cleaned DataFrame with standardized formats
    """
    # Create a copy to avoid pandas SettingWithCopyWarning
    df = df.copy()
    
    # Remove rows missing critical information
    df = df.dropna(subset=['Title', 'Price', 'Rating', 'Availability', 'URL'])
    
    # Convert Price from string with currency symbol to numeric value
    df.loc[:, 'Price'] = pd.to_numeric(df['Price'].str.replace('£', ''), errors='coerce')
    
    # Ensure Rating is numeric and within valid 1-5 star range
    df.loc[:, 'Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df = df[(df['Rating'] >= 1) & (df['Rating'] <= 5)]
    
    # Standardize Availability text to consistent values
    df.loc[:, 'Availability'] = df['Availability'].apply(lambda x: 'In Stock' if 'in stock' in str(x).lower() else 'Out of Stock')
    
    # Limit number of rows if exceeding configured maximum
    if len(df) > ProcessingConfig.MAX_ROWS:
        self.logger.warning(f"Truncating data to {ProcessingConfig.MAX_ROWS} rows")
        df = df.head(ProcessingConfig.MAX_ROWS)
    
    return df
```

## Key Features

1. **Robust Error Handling**
   - Comprehensive exception handling
   - Detailed logging for troubleshooting
   - Graceful failure mechanisms

2. **Data Validation and Cleaning**
   - Removal of incomplete data records
   - Type conversion and format standardization
   - Range validation for numeric fields

3. **Configurable Architecture**
   - External JSON configurations
   - Adjustable limits and thresholds
   - Environment-based configuration

4. **Automated Testing**
   - Unit tests for both scraping and processing
   - Edge case testing
   - Validation of output formats

## Extension Points

The project architecture supports several extension points:

1. **Additional Data Sources**
   - New scraper configurations can be added to `run_scrapper.json`
   - Multiple websites can be scraped without code changes

2. **Enhanced Processing**
   - Additional cleaning steps can be added to `_clean_data()`
   - New transformation rules can be implemented

3. **Output Formats**
   - Support for multiple output formats
   - Analytics-ready views

4. **Scheduling and Automation**
   - Lambda handler design supports integration with scheduling systems
   - Cloud deployment options
