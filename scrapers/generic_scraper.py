"""Generic scraper template for European PC component retailers."""

import re
from typing import List
from urllib.parse import urljoin

from scrapers.base_scraper import BaseScraper
from models.product import Product


class GenericRetailerScraper(BaseScraper):
    """Generic scraper that can be configured for different retailers."""
    
    def __init__(self, retailer_name: str, base_url: str,
                 ddr5_search_path: str, gpu_search_path: str,
                 selectors: dict):
        """
        Initialize generic scraper.
        
        Args:
            retailer_name: Name of the retailer
            base_url: Base URL of the retailer
            ddr5_search_path: Path for DDR5 RAM search
            gpu_search_path: Path for GPU search
            selectors: Dictionary of CSS selectors for elements
        """
        super().__init__(retailer_name, base_url)
        self.ddr5_search_path = ddr5_search_path
        self.gpu_search_path = gpu_search_path
        self.selectors = selectors
    
    def _extract_price(self, element) -> float:
        """Extract and parse price from element."""
        price_selector = self.selectors.get('price', '.price')
        price_elem = element.select_one(price_selector)
        
        if not price_elem:
            return 0.0
        
        price_text = price_elem.get_text(strip=True)
        # Remove non-numeric characters except comma and dot
        price_text = re.sub(r'[^\d,.]', '', price_text)
        # Replace comma with dot for European format
        price_text = price_text.replace(',', '.')
        
        try:
            return float(price_text)
        except ValueError:
            return 0.0
    
    def _scrape_category(self, search_path: str, category: str) -> List[Product]:
        """Generic method to scrape a product category."""
        products = []
        url = urljoin(self.base_url, search_path)
        
        soup = self.fetch_page(url)
        if not soup:
            return products
        
        # Find product containers
        container_selector = self.selectors.get('product_container', '.product')
        product_elements = soup.select(container_selector)
        
        for element in product_elements[:20]:  # Limit to first 20
            try:
                # Extract name
                name_selector = self.selectors.get('name', '.product-name')
                name_elem = element.select_one(name_selector)
                if not name_elem:
                    continue
                name = name_elem.get_text(strip=True)
                
                # Extract URL
                url_selector = self.selectors.get('url', 'a')
                url_elem = element.select_one(url_selector)
                if not url_elem:
                    continue
                product_url = urljoin(self.base_url, url_elem.get('href', ''))
                
                # Extract price
                price = self._extract_price(element)
                if price == 0.0:
                    continue
                
                # Check stock
                stock_selector = self.selectors.get('stock', '.stock-status')
                in_stock = True
                stock_elem = element.select_one(stock_selector)
                if stock_elem:
                    stock_text = stock_elem.get_text(strip=True).lower()
                    in_stock = 'out of stock' not in stock_text and 'unavailable' not in stock_text
                
                product = self.create_product(
                    name=name,
                    price=price,
                    url=product_url,
                    category=category,
                    in_stock=in_stock
                )
                products.append(product)
                
            except Exception as e:
                self.logger.warning(f"Error parsing product: {e}")
                continue
        
        return products
    
    def scrape_ddr5_ram(self) -> List[Product]:
        """Scrape DDR5 RAM products."""
        return self._scrape_category(self.ddr5_search_path, 'DDR5 RAM')
    
    def scrape_graphics_cards(self) -> List[Product]:
        """Scrape graphics card products."""
        return self._scrape_category(self.gpu_search_path, 'Graphics Card')
