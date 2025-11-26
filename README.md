# PC Deals Scraper 🛒

A Python web scraping bot that finds the best promotions for PC components (DDR5 RAM and Graphics Cards) across major European retailers.

## Features

- 🌍 **Multi-retailer support**: Amazon (DE, FR, ES, IT, UK), PCComponentes, LDLC, Alternate, Mindfactory
- 🎯 **Targeted scraping**: DDR5 RAM and Graphics Cards
- 📊 **Smart analysis**: Automatic deal comparison and best price detection
- 💾 **Multiple formats**: Export results as JSON or CSV
- 🔄 **Extensible**: Easy to add new retailers with the generic scraper template

## Supported Retailers

- **Amazon** (Germany, France, Spain, Italy, UK)
- **PCComponentes** (Spain)
- **LDLC** (France)
- **Alternate** (Germany)
- **Mindfactory** (Germany)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. Clone or navigate to the project directory:
```bash
cd pc-deals-scraper
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with default settings (all retailers, both output formats):
```bash
python main.py
```

### Command-Line Options

```bash
# Only scrape Amazon sites
python main.py --amazon-only

# Choose output format
python main.py --output json    # JSON only
python main.py --output csv     # CSV only
python main.py --output both    # Both formats (default)

# Enable verbose logging
python main.py --verbose

# Skip the summary display
python main.py --no-summary
```

### Example Commands

```bash
# Quick Amazon-only scrape with JSON output
python main.py --amazon-only --output json

# Full scrape with detailed logging
python main.py --verbose
```

## Output

Results are saved in the `output/` directory with timestamps:
- `deals_YYYYMMDD_HHMMSS.json` - JSON format
- `deals_YYYYMMDD_HHMMSS.csv` - CSV format

### Output Fields

- `name` - Product name
- `price` - Current price
- `original_price` - Original price (if discounted)
- `discount_percentage` - Discount percentage
- `savings` - Amount saved
- `retailer` - Retailer name
- `category` - Product category (DDR5 RAM / Graphics Card)
- `in_stock` - Stock availability
- `url` - Product URL
- `scraped_at` - Timestamp

## Project Structure

```
pc-deals-scraper/
├── main.py                 # Main application entry point
├── config.py              # Retailer configurations
├── requirements.txt       # Python dependencies
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py    # Base scraper class
│   ├── amazon_scraper.py  # Amazon-specific scraper
│   └── generic_scraper.py # Generic retailer scraper
├── models/
│   ├── __init__.py
│   └── product.py         # Product data model
├── utils/
│   ├── __init__.py
│   └── data_handler.py    # Data export and analysis utilities
├── tests/
│   └── __init__.py
└── output/                # Generated results (created automatically)
```

## Adding New Retailers

To add a new European retailer:

1. Open `config.py`
2. Add a new entry to `RETAILER_CONFIGS` with the retailer's information:

```python
'new_retailer': {
    'name': 'Retailer Name',
    'base_url': 'https://www.example.com',
    'ddr5_search_path': '/path/to/ddr5/search',
    'gpu_search_path': '/path/to/gpu/search',
    'selectors': {
        'product_container': '.product-card',
        'name': '.product-name',
        'price': '.price',
        'url': 'a',
        'stock': '.stock-status'
    }
}
```

3. Test the scraper to verify the CSS selectors are correct

## Customization

### Scraping Limits

Edit `config.py` to adjust:
- `MAX_PRODUCTS_PER_CATEGORY` - Products per category (default: 20)
- `REQUEST_TIMEOUT` - HTTP request timeout (default: 10s)
- `MAX_RETRIES` - Retry attempts (default: 3)

### Amazon Countries

Edit the `AMAZON_COUNTRIES` list in `config.py` to add/remove Amazon sites.

## Notes

- **Respect robots.txt**: This scraper should be used responsibly
- **Rate limiting**: Built-in delays prevent overwhelming servers
- **Selectors may change**: Websites update their HTML; selectors may need updates
- **Legal**: For personal/educational use only

## Troubleshooting

### No products found
- Check internet connection
- Verify website accessibility
- Update CSS selectors if site structure changed

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment if using one

### Timeout errors
- Increase `REQUEST_TIMEOUT` in `config.py`
- Check network stability

## Future Enhancements

- [ ] Price tracking over time
- [ ] Email notifications for deals
- [ ] Database storage
- [ ] Web dashboard
- [ ] More retailers
- [ ] Additional product categories

## License

This project is for educational purposes only.
