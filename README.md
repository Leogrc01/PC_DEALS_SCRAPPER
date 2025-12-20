# PC Deals Scraper 🛒

A Python web scraping bot that finds the best Black Friday deals on PC components (DDR5 RAM and Graphics Cards) across Amazon Europe.

## Features

- 🌍 **Amazon Europe**: 5 markets (DE, FR, ES, IT, UK)
- 🎯 **Smart filtering**: DDR5 RAM (Desktop) and Graphics Cards only
- 💰 **Black Friday deals**: Captures discounts with original prices and percentages
- 📊 **Grouped reports**: Products sorted by exact model (RTX 4060, RTX 4070 Ti, etc.)
- 💾 **Multiple formats**: JSON, CSV, and Markdown reports
- ⚡ **Fast**: ~100 products in 30 seconds
- 🚀 **Simple**: One command to run everything

## Quick Start

```bash
# First time setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the scraper
./scrape.sh
```

That's it! Results are saved in `output/` folder.

## What You Get

### 1. **Grouped Markdown Report** (`grouped_deals_*.md`) ⭐

Products organized by exact model with discounts highlighted:

```markdown
### RTX 3050 8GB
- ~~€254.90~~ **€169.00** (-33.7%) — MSI GeForce RTX 3050...

### RTX 5070 Ti 16GB  
- ~~€999.99~~ **€794.99** (-20.5%) — Gigabyte GeForce...
```

### 2. **Top 5 Deals in Terminal**

Automatically displayed after scraping:
```
💰 TOP 5 MEILLEURS DEALS:
1. RTX 3050: €254.90 → €169.00 (-33.7%)
2. RTX 5060: €379.00 → €269.00 (-29.0%)
...
```

### 3. **JSON & CSV Files**

For data analysis and spreadsheets.

## Supported Products

### Graphics Cards
- **NVIDIA RTX 30xx**: 3050, 3060, 3070, 3080, 3090 (all variants)
- **NVIDIA RTX 40xx**: 4060, 4060 Ti, 4070, 4070 Super, 4080, 4090
- **NVIDIA RTX 50xx**: 5060, 5070, 5080, 5090 (Ti/Super variants)
- **AMD Radeon RX**: 6xxx, 7xxx, 9xxx series

### DDR5 RAM
- Desktop RAM only (SODIMM/laptop RAM filtered out)
- All capacities: 8GB to 128GB
- All speeds: 4800MHz to 8400MHz+

### Automatic Filtering

Accessories automatically excluded:
- ❌ GPU supports, brackets, risers
- ❌ Cooling solutions, fans
- ❌ Cables, adapters
- ❌ RGB lighting kits
- ❌ Laptop RAM (SODIMM)

## Usage

### One-Time Scraping

```bash
# Simple way
./scrape.sh

# Manual with options
python main.py --amazon-only --grouped-report
python main.py --amazon-only --output json --verbose
```

### 🔔 Monitoring Mode (RAM Availability Alerts)

**Perfect for RAM shortages!** Leave it running to get instant notifications when RAM is available.

```bash
# Activate venv first
source venv/bin/activate

# Start monitoring (checks every 5 minutes)
python monitor.py

# With price limit (max 150€)
python monitor.py --max-price 150

# Only 32GB+ RAM, check every 2 minutes
python monitor.py --min-capacity 32 --interval 120

# Silent mode (visual notifications only)
python monitor.py --no-sound

# Stop with Ctrl+C
```

**What you get:**
- 🔔 **macOS notifications** with sound when RAM is in stock
- 🗣️ **Text-to-speech** announcements ("RAM disponible à 129 euros")
- 🚚 **Delivery sorting**: products sorted by fastest delivery first (today → tomorrow → specific dates)
- 🌍 **Multilingual parsing**: detects delivery dates in EN, FR, DE, ES, IT
- 🎯 **Smart filtering**: price limit + capacity filter
- 🚫 **No spam**: tracks notified products (won't alert twice)
- 💾 **Persistent cache**: remembers between runs
- 🔄 **Continuous scanning**: all Amazon EU sites every N minutes

**Monitoring Options:**
```
--max-price PRICE      Maximum price in EUR (e.g., 150)
--interval SECONDS     Check interval (default: 300 = 5 min)
--min-capacity GB      Minimum RAM capacity (default: 16GB)
--no-sound             Disable sound (visual only)
--reset-cache          Re-alert for all products
--verbose              Show detailed logs
```

## Output Files

### Grouped Markdown Report (`grouped_deals_*.md`) ⭐

Best for browsing deals:
- Products grouped by exact model (RTX 3060, RTX 4070 Ti, etc.)
- Sorted by price within each group
- Discounts highlighted: ~~€999~~ **€799** (-20%)
- Direct Amazon links (/dp/{ASIN})

### JSON (`deals_*.json`)

For programmatic access:
```json
{
  "name": "MSI GeForce RTX 3050...",
  "price": 169.0,
  "original_price": 254.9,
  "discount_percentage": 33.7,
  "savings": 85.9,
  "retailer": "Amazon ES",
  "category": "Graphics Card",
  "url": "https://www.amazon.es/dp/..."
}
```

### CSV (`deals_*.csv`)

For Excel/Google Sheets analysis.

## Project Structure

```
pc-deals-scraper/
├── scrape.sh              # 🚀 Simple launcher script
├── main.py                # Main application
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── UTILISATION.md         # Quick guide (French)
├── WARP.md                # Development guide
├── scrapers/
│   ├── base_scraper.py    # Base scraper class
│   ├── amazon_scraper.py  # Amazon scraper with deals extraction
│   └── generic_scraper.py # Generic retailer scraper
├── models/
│   └── product.py         # Product data model
├── utils/
│   └── data_handler.py    # Data export & grouping
└── output/                # 📊 Generated results
    ├── deals_*.json
    ├── deals_*.csv
    └── grouped_deals_*.md  # ⭐ Best for browsing
```

## Why Amazon Only?

Other European retailers (LDLC, Alternate, Mindfactory, PCComponentes) use:
- ❌ JavaScript to load products dynamically
- ❌ Strong anti-bot protections (Cloudflare, Datadome)
- ❌ Requiring browser automation (slow & fragile)

Amazon provides:
- ✅ Server-side rendering (fast scraping)
- ✅ 5 European markets
- ✅ Consistent HTML structure
- ✅ ~100 products found
- ✅ Reliable deal detection

## Configuration

Edit `config.py` to customize:

```python
# Amazon markets to scrape
AMAZON_COUNTRIES = ['de', 'fr', 'es', 'it', 'co.uk']

# Results per category
MAX_PRODUCTS_PER_CATEGORY = 20

# HTTP settings
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
```

## Performance

- **Speed**: ~30 seconds for complete scan
- **Products**: ~100 items (29 GPUs + 69 RAM modules)
- **Success rate**: 95%+ (occasionally Amazon blocks)
- **Markets**: 5 countries simultaneously

## Notes

- 🤖 Respectful scraping with delays and retries
- 📜 For personal/educational use only
- 🔄 CSS selectors may need updates if Amazon changes HTML
- 🛡️ Uses standard HTTP requests (no browser automation)

## Troubleshooting

### "No products found"
```bash
# Check if Amazon is accessible
curl -I https://www.amazon.fr

# Try with verbose logging
python main.py --amazon-only --verbose
```

### "Module not found" errors
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Scraper is slow
- Normal! ~30 seconds for 5 Amazon markets
- Amazon has rate limiting
- Each market is scraped sequentially

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parser
- `pandas` - CSV export
- `python-dotenv` - Environment variables

Python 3.8+ required (tested on 3.14)

## License

This project is for educational purposes only. Use responsibly and respect Amazon's Terms of Service.
