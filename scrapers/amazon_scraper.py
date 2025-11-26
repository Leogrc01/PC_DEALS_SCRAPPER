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
            '.a-price .a-offscreen',
            'span.a-price span.a-offscreen',
            '.a-price-whole'
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
        search_url = f"{self.base_url}/s?k=DDR5+RAM"
        
        soup = self.fetch_page(search_url)
        if not soup:
            return products
        
        # Find product cards
        product_cards = soup.select('[data-component-type="s-search-result"]')
        
        self.logger.debug(f"Found {len(product_cards)} product cards")
        
        for card in product_cards[:20]:  # Limit to first 20 results
            try:
                # Skip sponsored products without ASIN
                asin = card.get('data-asin', '')
                if not asin:
                    self.logger.debug("Skipping card: no ASIN")
                    continue
                
                # Extract product name
                name_elem = card.select_one('h2 span')
                if not name_elem:
                    self.logger.debug(f"Skipping ASIN {asin}: no title found")
                    continue
                name = name_elem.get_text(strip=True)
                
                # Filter out accessories (GPU supports, cooling, brackets, etc.)
                name_lower = name.lower()
                excluded_keywords = ['support', 'bracket', 'halterung', 'cooling', 'refroidissement', 
                                   'ventilateur', 'fan', 'stand', 'holder', 'soporte', 'supporto',
                                   'kühlkörper', 'dissipateur', 'raffreddatore', 'nas storage', 'nas-speicher',
                                   'diskstation', 'anti-affaissement', 'aufbewahrung', 'koffer',
                                   'case', 'coffret', 'cavo', 'cable', 'kabel', 'câble',
                                   'adattatore', 'adapter', 'convertitore', 'tester', 'testeur',
                                   'heatsink', 'heat sink', 'iluminación', 'lighting', 'led strip',
                                   'argb', 'rgb strip', 'light enhancement', 'enhancement kit',
                                   'potenziamento della luce', 'mejora de la iluminación',
                                   'sodimm', 'so-dimm', 'laptop', 'notebook', 'portatile',
                                   'ordenador portátil', 'portable', 'portátil']
                if any(keyword in name_lower for keyword in excluded_keywords):
                    self.logger.debug(f"Skipping {name[:30]}: accessory/non-RAM product")
                    continue
                
                # Build direct product URL from ASIN
                url = f"{self.base_url}/dp/{asin}"
                
                # Extract price
                price = self._extract_price(card)
                if price == 0.0:
                    self.logger.debug(f"Skipping {name[:30]}: no valid price found")
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
        search_url = f"{self.base_url}/s?k=RTX+4060+4070+4080+4090"
        
        soup = self.fetch_page(search_url)
        if not soup:
            return products
        
        # Find product cards
        product_cards = soup.select('[data-component-type="s-search-result"]')
        
        for card in product_cards[:20]:  # Limit to first 20 results
            try:
                # Skip sponsored products without ASIN
                asin = card.get('data-asin', '')
                if not asin:
                    continue
                
                # Extract product name
                name_elem = card.select_one('h2 span')
                if not name_elem:
                    continue
                name = name_elem.get_text(strip=True)
                
                # Filter out accessories (GPU supports, cooling, brackets, etc.)
                name_lower = name.lower()
                excluded_keywords = ['support', 'bracket', 'halterung', 'cooling', 'refroidissement',
                                   'ventilateur', 'fan', 'stand', 'holder', 'soporte', 'supporto',
                                   'kühlkörper', 'dissipateur', 'riser', 'cable', 'kabel', 'câble',
                                   'anti-affaissement', 'anti-sag', 'aufbewahrung', 'koffer',
                                   'case', 'coffret', 'cavo', 'adattatore', 'adapter', 'adaptador',
                                   'convertitore', 'frame', 'rahmen', 'cadre', 'chargeur', 'charger',
                                   'netzteil', 'alimentatore', 'power supply', 'lenovo', 'laptop',
                                   'arm', 'bras', 'braccio', 'pcie adapter', 'pcie 5.']
                if any(keyword in name_lower for keyword in excluded_keywords):
                    self.logger.debug(f"Skipping {name[:30]}: accessory/non-GPU product")
                    continue
                
                # Build direct product URL from ASIN
                url = f"{self.base_url}/dp/{asin}"
                
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
