"""Configuration for retailers and scraping parameters."""

# European Amazon sites to scrape
AMAZON_COUNTRIES = ['de', 'fr', 'es', 'it', 'co.uk']

# Example configurations for other European retailers
# These are templates - actual selectors need to be verified for each site
RETAILER_CONFIGS = {
    'ldlc': {
        'name': 'LDLC',
        'base_url': 'https://www.ldlc.com',
        'ddr5_search_path': '/informatique/pieces-informatique/memoire-pc/c4293/+fv1026-19320.html',
        'gpu_search_path': '/informatique/pieces-informatique/carte-graphique-interne/c4684/',
        'selectors': {
            'product_container': '.listing-product',
            'name': '.title-3',
            'price': '.price',
            'url': 'a.pdt-item',
            'stock': '.stock'
        }
    },
    'alternate': {
        'name': 'Alternate',
        'base_url': 'https://www.alternate.de',
        'ddr5_search_path': '/listing.xhtml?q=ddr5',
        'gpu_search_path': '/listing.xhtml?q=nvidia+rtx+40',
        'selectors': {
            'product_container': '.card.product-card',
            'name': '.card-title',
            'price': '.price',
            'url': 'a',
            'stock': '.delivery-info'
        }
    },
    'mindfactory': {
        'name': 'Mindfactory',
        'base_url': 'https://www.mindfactory.de',
        'ddr5_search_path': '/Hardware/Arbeitsspeicher+(RAM)/DDR5.html',
        'gpu_search_path': '/Hardware/Grafikkarten+(VGA)/GeForce+RTX+40xx.html',
        'selectors': {
            'product_container': '.pcontent',
            'name': '.pname',
            'price': '.pprice',
            'url': 'a',
            'stock': '.pavail'
        }
    },
    'pccomponentes': {
        'name': 'PCComponentes',
        'base_url': 'https://www.pccomponentes.com',
        'ddr5_search_path': '/memorias-ram/ddr5',
        'gpu_search_path': '/tarjetas-graficas',
        'selectors': {
            'product_container': 'article.tarjeta-articulo',
            'name': '.articulo-nombre',
            'price': '.precio-actual',
            'url': 'a',
            'stock': '.availability'
        }
    }
}

# Scraping settings
MAX_PRODUCTS_PER_CATEGORY = 20
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3

# Output settings
OUTPUT_DIR = 'output'
OUTPUT_FORMAT = 'json'  # Options: 'json', 'csv', 'both'
