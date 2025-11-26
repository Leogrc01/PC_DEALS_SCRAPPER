"""Amazon scraper for European Amazon sites."""

import re
from typing import List
from urllib.parse import urljoin

from scrapers.base_scraper import BaseScraper
from models.product import Product


class AmazonScraper(BaseScraper):
    """Scraper for Amazon European stores."""
    
    def __init__(self, country_code: str = 'de'):
        """
        Initialize Amazon scraper.
        
        Args:
            country_code: Amazon country code (de, fr, es, it, uk)
        """
        base_url = f"https://www.amazon.{country_code}"
        super().__init__(f"Amazon {country_code.upper()}", base_url)
        self.country_code = country_code
    
    def _extract_price(self, soup) -> float:
        """Extract price from product element."""
        price_selectors = [
            '.a-price-whole',
            '.a-offscreen',
            'span.a-price span.a-offscreen'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Remove currency symbols and convert comma to dot
                price_text = re.sub(r'[^\d,.]', '', price_text)
                price_text = price_text.replace(',', '.')
                try:
                    return float(price_text)
                except ValueError:
                    continue
        return 0.0
    
    def scrape_ddr5_ram(self) -> List[Product]:
        """Scrape DDR5 RAM from Amazon."""
        products = []
        search_url = f"{self.base_url}/s?k=DDR5+RAM&rh=n:340509031"
        
        soup = self.fetch_page(search_url)
        if not soup:
            return products
        
        # Find product cards
        product_cards = soup.select('[data-component-type="s-search-result"]')
        
        for card in product_cards[:20]:  # Limit to first 20 results
            try:
                # Extract product name
                name_elem = card.select_one('h2 a span')
                if not name_elem:
                    continue
                name = name_elem.get_text(strip=True)
                
                # Extract URL
                url_elem = card.select_one('h2 a')
                if not url_elem:
                    continue
                url = urljoin(self.base_url, url_elem.get('href', ''))
                
                # Extract price
                price = self._extract_price(card)
                if price == 0.0:
                    continue
                
                # Check stock
                in_stock = 'Currently unavailable' not in card.get_text()
                
                product = self.create_product(
                    name=name,
                    price=price,
                    url=url,
                    category='DDR5 RAM',
                    in_stock=in_stock
                )
                products.append(product)
                
            except Exception as e:
                self.logger.warning(f"Error parsing product: {e}")
                continue
        
        return products
    
    def scrape_graphics_cards(self) -> List[Product]:
        """Scrape graphics cards from Amazon."""
        products = []
        search_url = f"{self.base_url}/s?k=graphics+card+RTX+4060+4070+4080+4090&rh=n:430161031"
        
        soup = self.fetch_page(search_url)
        if not soup:
            return products
        
        # Find product cards
        product_cards = soup.select('[data-component-type="s-search-result"]')
        
        for card in product_cards[:20]:  # Limit to first 20 results
            try:
                # Extract product name
                name_elem = card.select_one('h2 a span')
                if not name_elem:
                    continue
                name = name_elem.get_text(strip=True)
                
                # Extract URL
                url_elem = card.select_one('h2 a')
                if not url_elem:
                    continue
                url = urljoin(self.base_url, url_elem.get('href', ''))
                
                # Extract price
                price = self._extract_price(card)
                if price == 0.0:
                    continue
                
                # Check stock
                in_stock = 'Currently unavailable' not in card.get_text()
                
                product = self.create_product(
                    name=name,
                    price=price,
                    url=url,
                    category='Graphics Card',
                    in_stock=in_stock
                )
                products.append(product)
                
            except Exception as e:
                self.logger.warning(f"Error parsing product: {e}")
                continue
        
        return products
