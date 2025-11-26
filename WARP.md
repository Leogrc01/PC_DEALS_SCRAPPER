# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Current Status

**Working**: Amazon scrapers for all European sites (DE, FR, ES, IT, UK)
**Other retailers**: LDLC, Alternate, Mindfactory, PCComponentes are not supported (require Selenium + have strong anti-bot protections)

**Focus**: Amazon provides excellent European coverage across 5 markets with 80+ products

## Development Commands

### Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Scraper
```bash
# Amazon-only scraping (RECOMMENDED - other retailers currently disabled)
python main.py --amazon-only

# Basic usage (only Amazon works currently)
python main.py

# Specific output format
python main.py --output json
python main.py --output csv

# Verbose logging
python main.py --verbose

# Skip summary display
python main.py --no-summary

# Generate grouped Markdown report (by GPU series/VRAM and RAM capacity)
python main.py --amazon-only --grouped-report

# Combined options
python main.py --amazon-only --output json --verbose
```

### Testing
This project currently doesn't have a test suite defined. When adding tests:
- Place test files in the `tests/` directory
- Use pytest as the testing framework (add to requirements.txt if needed)
- Run with `pytest tests/`

## Architecture Overview

### Core Design Pattern
The codebase uses an **object-oriented scraper architecture** with a base class and specialized implementations:

- **`BaseScraper`** (abstract base class): Provides common functionality for all scrapers
  - HTTP session management with retries and exponential backoff
  - Page fetching with error handling
  - Abstract methods for category-specific scraping (`scrape_ddr5_ram`, `scrape_graphics_cards`)
  - Unified `scrape_all()` method that orchestrates both categories

- **`AmazonScraper`**: Specialized for Amazon's HTML structure across multiple European domains
  - Handles country-specific URLs (de, fr, es, it, co.uk)
  - Custom price extraction logic for Amazon's complex price elements
  - Uses Amazon-specific CSS selectors

- **`GenericRetailerScraper`**: Configuration-driven scraper for other retailers
  - Accepts retailer configuration from `config.py`
  - Uses configurable CSS selectors defined per retailer
  - Single implementation works for LDLC, Alternate, Mindfactory, PCComponentes

### Data Flow
1. **Entry Point** (`main.py`): CLI argument parsing, logging setup, orchestration
2. **Scrapers** (`scrapers/`): Fetch and parse HTML from retailers
3. **Product Model** (`models/product.py`): Dataclass representing products with computed properties (discount_percentage, savings)
4. **Data Handler** (`utils/data_handler.py`): Filtering, sorting, statistics, and export (JSON/CSV)
5. **Output** (`output/`): Timestamped files with scraped results

### Key Components

**Configuration (`config.py`)**:
- `AMAZON_COUNTRIES`: List of Amazon country codes to scrape
- `RETAILER_CONFIGS`: Dictionary defining each retailer's base URL, search paths, and CSS selectors
- `MAX_PRODUCTS_PER_CATEGORY`: Limit results per category (default: 20)
- `REQUEST_TIMEOUT` and `MAX_RETRIES`: HTTP request settings

**Product Model**:
- Uses Python dataclasses with computed properties
- Automatically calculates discount percentages and savings
- `to_dict()` method for serialization

**Error Handling**:
- Exponential backoff for HTTP retries
- Per-retailer error isolation (one retailer failure doesn't stop others)
- Logging at multiple levels (INFO, WARNING, ERROR, DEBUG)

### Product Filtering
- Accessories (GPU supports, cooling, cables, etc.) are automatically filtered out
- Filter keywords are maintained in `scrapers/amazon_scraper.py`
- Filters are multilingual (English, French, German, Spanish, Italian)

## Adding New Retailers

**Note**: Most European retailers use JavaScript to load products dynamically and require Selenium implementation.

To add a European retailer:

1. Add configuration to `RETAILER_CONFIGS` in `config.py`:
```python
'retailer_id': {
    'name': 'Retailer Name',
    'base_url': 'https://www.example.com',
    'ddr5_search_path': '/path/to/ddr5',
    'gpu_search_path': '/path/to/gpu',
    'selectors': {
        'product_container': '.css-selector',
        'name': '.name-selector',
        'price': '.price-selector',
        'url': 'a',
        'stock': '.stock-selector'
    }
}
```

2. Test by running `python main.py` - the new retailer will automatically be scraped via `GenericRetailerScraper`

## Important Notes

### CSS Selectors
- Selectors are fragile and break when retailers update their HTML
- When debugging selector issues, use browser DevTools to inspect current HTML structure
- Amazon selectors are particularly complex due to A/B testing and regional variations
- Current working selectors for Amazon:
  - Product container: `[data-component-type="s-search-result"]`
  - Title: `h2 span`
  - Price: `.a-price .a-offscreen`
  - URL: `a.a-link-normal`

### Rate Limiting
- Built-in delays and retry logic prevent overwhelming servers
- Scraping is synchronous (one retailer at a time)
- Respect each retailer's robots.txt

### Price Parsing
- European format uses commas as decimal separators (€19,99)
- Price extraction removes currency symbols and normalizes to float
- Original prices (for discount calculation) are optional

### Output Files
- Automatically saved to `output/` directory with timestamp format: `deals_YYYYMMDD_HHMMSS.{json,csv}`
- CSV includes column reordering for readability
- JSON preserves full data structure with proper encoding
- **Grouped report** (optional): `grouped_deals_YYYYMMDD_HHMMSS.md` - Products organized by:
  - Graphics Cards: by series and VRAM (e.g., "RTX 30xx 8G", "RTX 40xx 16G", "RX 7xxx 16G")
  - DDR5 RAM: by total capacity (e.g., "16GB", "32GB", "64GB")
  - Each group sorted by price (lowest first)

## Dependency Management
- Python 3.8+ required
- Key dependencies: `requests`, `beautifulsoup4`, `pandas`, `selenium`
- `selenium` is included but not currently used (reserved for JavaScript-heavy sites)
- Always use virtual environments to isolate dependencies
