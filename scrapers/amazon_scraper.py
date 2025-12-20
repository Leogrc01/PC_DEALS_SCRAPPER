"""Amazon scraper for European Amazon sites."""

import re
from typing import List, Optional, Tuple
from urllib.parse import urljoin
from datetime import datetime, timedelta

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
    
    def _extract_original_price(self, card) -> float:
        """Extract original/recommended price (crossed out price) if available."""
        # Try different selectors for original price
        original_selectors = [
            '.a-price.a-text-price .a-offscreen',  # Recommended price
            'span.a-price.a-text-price span.a-offscreen',
            '.a-text-strike .a-offscreen'
        ]
        
        for selector in original_selectors:
            orig_elem = card.select_one(selector)
            if orig_elem:
                price_text = orig_elem.get_text(strip=True)
                price_text = re.sub(r'[^\d,.]', '', price_text)
                price_text = price_text.replace(',', '.')
                try:
                    return float(price_text)
                except ValueError:
                    continue
        return None
    
    def _is_available_now(self, card) -> bool:
        """Check if product is available for immediate purchase (not preorder, not long delays)."""
        card_text = card.get_text()
        card_text_lower = card_text.lower()
        
        # Explicit unavailability indicators
        unavailable_keywords = [
            'currently unavailable',
            'actuellement indisponible',
            'derzeit nicht verfügbar',
            'non disponibile',
            'no disponible',
            'out of stock',
            'rupture de stock',
            'nicht auf lager',
            'esaurito'
        ]
        
        for keyword in unavailable_keywords:
            if keyword in card_text_lower:
                self.logger.debug(f"Product unavailable (keyword: {keyword})")
                return False
        
        # Check for future years (2026, 2027, etc.)
        import datetime
        current_year = datetime.datetime.now().year
        for year in range(current_year + 1, current_year + 5):  # Check next 4 years
            if str(year) in card_text:
                self.logger.debug(f"Product delivery in future year: {year}")
                return False
        
        # Preorder indicators
        preorder_keywords = [
            'preorder',
            'pre-order',
            'précommande',
            'vorbestell',
            'preordine',
            'disponible le',  # French: "available on [date]"
            'verfügbar ab',   # German: "available from [date]"
            'disponibile dal', # Italian: "available from [date]"
            'disponible a partir',  # Spanish
            'coming soon',
            'bientôt disponible',
            'demnächst',
            'pré-commande',
            'date de sortie',  # French: "release date"
            'en prévente',     # French: "in presale"
            'date de livraison prévue',  # French: "expected delivery date"
        ]
        
        for keyword in preorder_keywords:
            if keyword in card_text_lower:
                self.logger.debug(f"Product is preorder (keyword: {keyword})")
                return False
        
        # Long delay months (>1 month from December)
        # Currently December 2024, so filter Feb+ (>1 month away)
        far_future_months = [
            # French (Feb-Dec, excluding Jan which is acceptable)
            'février', 'mars', 'avril', 'mai', 'juin',
            'juillet', 'août', 'septembre', 'octobre', 'novembre',
            # English
            'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november',
            # German
            'februar', 'märz', 'april', 'mai', 'juni',
            'juli', 'august', 'september', 'oktober', 'november',
            # Spanish
            'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre',
            # Italian
            'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
            'luglio', 'agosto', 'settembre', 'ottobre', 'novembre',
        ]
        
        for month in far_future_months:
            if month in card_text_lower:
                self.logger.debug(f"Product has long delivery delay (month: {month})")
                return False
        
        # Long delivery delay indicators (more than 1 month)
        long_delay_keywords = [
            'mois',  # French months
            'monat', # German months
            'mes',   # Spanish/Italian months (e.g., "2 meses")
            'weeks', 'semaines', 'wochen', 'settimane', 'semanas',
        ]
        
        # Check for delivery mentions with long delays
        delivery_section = ''
        delivery_elem = card.select_one('[data-cy="delivery-recipe"]')
        if delivery_elem:
            delivery_section = delivery_elem.get_text().lower()
        
        for keyword in long_delay_keywords:
            if keyword in delivery_section:
                # If mentioning weeks/months in delivery, likely too long
                return False
        
        return True
    
    def _extract_delivery_info(self, card) -> Tuple[Optional[datetime], Optional[str]]:
        """Extract delivery date and text from product card.
        
        Returns:
            Tuple of (delivery_date, delivery_text)
        """
        delivery_elem = card.select_one('[data-cy="delivery-recipe"]')
        if not delivery_elem:
            # Try alternative selectors
            delivery_elem = card.select_one('.s-shipping-fast-text, .s-prime-shipping-label, .s-delivery-message')
        
        if not delivery_elem:
            return None, None
        
        delivery_text = delivery_elem.get_text(strip=True)
        delivery_text_lower = delivery_text.lower()
        
        # Parse delivery date from text
        delivery_date = None
        today = datetime.now()
        
        # Patterns for "tomorrow" in all EU languages
        tomorrow_keywords = [
            'tomorrow',           # English (UK)
            'demain',            # French
            'mañana',            # Spanish
            'domani',            # Italian
            'morgen',            # German
        ]
        if any(kw in delivery_text_lower for kw in tomorrow_keywords):
            delivery_date = today + timedelta(days=1)
        
        # Patterns for "today" in all EU languages
        today_keywords = [
            'today',             # English (UK)
            "aujourd'hui",      # French
            'hoy',               # Spanish
            'oggi',              # Italian
            'heute',             # German
        ]
        if any(kw in delivery_text_lower for kw in today_keywords):
            delivery_date = today
        
        # Patterns for days (e.g., "Monday", "lundi", etc.)
        # This handles cases like "Get it by Monday" / "Reçois-le lundi"
        weekday_patterns = {
            # Monday
            'monday': 0, 'lundi': 0, 'lunes': 0, 'lunedì': 0, 'montag': 0,
            # Tuesday
            'tuesday': 1, 'mardi': 1, 'martes': 1, 'martedì': 1, 'dienstag': 1,
            # Wednesday
            'wednesday': 2, 'mercredi': 2, 'miércoles': 2, 'mercoledì': 2, 'mittwoch': 2,
            # Thursday
            'thursday': 3, 'jeudi': 3, 'jueves': 3, 'giovedì': 3, 'donnerstag': 3,
            # Friday
            'friday': 4, 'vendredi': 4, 'viernes': 4, 'venerdì': 4, 'freitag': 4,
            # Saturday
            'saturday': 5, 'samedi': 5, 'sábado': 5, 'sabato': 5, 'samstag': 5,
            # Sunday
            'sunday': 6, 'dimanche': 6, 'domingo': 6, 'domenica': 6, 'sonntag': 6,
        }
        
        for day_name, weekday_num in weekday_patterns.items():
            if day_name in delivery_text_lower:
                # Calculate next occurrence of this weekday
                current_weekday = today.weekday()
                days_ahead = weekday_num - current_weekday
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                delivery_date = today + timedelta(days=days_ahead)
                break
        
        # Look for specific dates (e.g., "Dec 21", "21 déc.", "21. Dez")
        # Extended month patterns for all EU languages
        day_match = re.search(
            r'\b(\d{1,2})\s*(?:' 
            # English (UK)
            r'jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|' 
            # French
            r'janv|févr|mars|avr|mai|juin|juil|août|sept|oct|nov|déc|' 
            # Spanish
            r'ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic|' 
            # Italian
            r'gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic|' 
            # German
            r'jan|feb|mär|apr|mai|jun|jul|aug|sep|okt|nov|dez' 
            r')\.?', 
            delivery_text_lower
        )
        
        if day_match:
            day = int(day_match.group(1))
            # Assume it's the nearest occurrence of that day
            # Simple heuristic: if day < today's day, assume next month, else this month
            if day < today.day:
                # Next month
                if today.month == 12:
                    delivery_date = datetime(today.year + 1, 1, day)
                else:
                    try:
                        delivery_date = datetime(today.year, today.month + 1, day)
                    except ValueError:
                        # Day doesn't exist in next month (e.g., 31 in Feb)
                        delivery_date = None
            else:
                # This month
                try:
                    delivery_date = datetime(today.year, today.month, day)
                except ValueError:
                    # Day doesn't exist in current month
                    delivery_date = None
        
        return delivery_date, delivery_text
    
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
                
                # Extract original price if available (for deals)
                original_price = self._extract_original_price(card)
                
                # Check stock (improved: excludes preorders and long delays)
                in_stock = self._is_available_now(card)
                
                # Extract delivery information
                delivery_date, delivery_text = self._extract_delivery_info(card)
                
                product = self.create_product(
                    name=name,
                    price=price,
                    url=url,
                    category='DDR5 RAM',
                    in_stock=in_stock,
                    original_price=original_price
                )
                product.delivery_date = delivery_date
                product.delivery_text = delivery_text
                products.append(product)
                
            except Exception as e:
                self.logger.warning(f"Error parsing product: {e}")
                continue
        
        return products
    
    def scrape_cpus(self) -> List[Product]:
        """Scrape CPUs from Amazon."""
        products = []
        # Search for Intel and AMD CPUs
        search_url = f"{self.base_url}/s?k=Intel+Core+i5+i7+i9+AMD+Ryzen+5+7+9"
        
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
                
                # Filter out accessories (coolers, thermal paste, etc.)
                name_lower = name.lower()
                excluded_keywords = ['cooler', 'ventirad', 'kühler', 'dissipatore',
                                   'thermal paste', 'pâte thermique', 'wärmeleitpaste',
                                   'fan', 'ventilateur', 'lüfter', 'ventola',
                                   'motherboard', 'carte mère', 'mainboard', 'scheda madre',
                                   'kit upgrade', 'bundle', 'pc complet', 'barebone']
                if any(keyword in name_lower for keyword in excluded_keywords):
                    self.logger.debug(f"Skipping {name[:30]}: accessory/non-CPU product")
                    continue
                
                # Only keep products with CPU indicators
                cpu_keywords = ['intel', 'amd', 'ryzen', 'core i', 'processor', 'processeur', 'prozessor', 'processore']
                if not any(keyword in name_lower for keyword in cpu_keywords):
                    continue
                
                # Build direct product URL from ASIN
                url = f"{self.base_url}/dp/{asin}"
                
                # Extract price
                price = self._extract_price(card)
                if price == 0.0:
                    continue
                
                # Extract original price if available (for deals)
                original_price = self._extract_original_price(card)
                
                # Check stock (improved: excludes preorders and long delays)
                in_stock = self._is_available_now(card)
                
                product = self.create_product(
                    name=name,
                    price=price,
                    url=url,
                    category='CPU',
                    in_stock=in_stock,
                    original_price=original_price
                )
                products.append(product)
                
            except Exception as e:
                self.logger.warning(f"Error parsing product: {e}")
                continue
        
        return products
    
    def scrape_graphics_cards(self) -> List[Product]:
        """Scrape graphics cards from Amazon."""
        products = []
        # Search for all RTX generations
        search_url = f"{self.base_url}/s?k=RTX+3060+3070+3080+3090+4060+4070+4080+4090+5060+5070+5080+5090"
        
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
                
                # Extract original price if available (for deals)
                original_price = self._extract_original_price(card)
                
                # Check stock (improved: excludes preorders and long delays)
                in_stock = self._is_available_now(card)
                
                product = self.create_product(
                    name=name,
                    price=price,
                    url=url,
                    category='Graphics Card',
                    in_stock=in_stock,
                    original_price=original_price
                )
                products.append(product)
                
            except Exception as e:
                self.logger.warning(f"Error parsing product: {e}")
                continue
        
        return products
