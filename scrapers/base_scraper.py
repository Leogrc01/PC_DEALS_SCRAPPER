"""Base scraper class providing common functionality for all retailer scrapers."""

import logging
import time
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from models.product import Product


class BaseScraper(ABC):
    """Abstract base class for all product scrapers."""
    
    def __init__(self, retailer_name: str, base_url: str):
        """
        Initialize the scraper.
        
        Args:
            retailer_name: Name of the retailer
            base_url: Base URL of the retailer's website
        """
        self.retailer_name = retailer_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.logger = logging.getLogger(f"{__name__}.{retailer_name}")
        
    def fetch_page(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetch a webpage with retries.
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts
            
        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
    
    @abstractmethod
    def scrape_ddr5_ram(self) -> List[Product]:
        """
        Scrape DDR5 RAM products.
        
        Returns:
            List of Product objects
        """
        pass
    
    @abstractmethod
    def scrape_graphics_cards(self) -> List[Product]:
        """
        Scrape graphics card products.
        
        Returns:
            List of Product objects
        """
        pass
    
    @abstractmethod
    def scrape_cpus(self) -> List[Product]:
        """
        Scrape CPU products.
        
        Returns:
            List of Product objects
        """
        pass
    
    def scrape_all(self) -> List[Product]:
        """
        Scrape all product categories.
        
        Returns:
            Combined list of all products
        """
        products = []
        
        self.logger.info(f"Starting scrape for {self.retailer_name}")
        
        # Scrape DDR5 RAM
        self.logger.info("Scraping DDR5 RAM...")
        products.extend(self.scrape_ddr5_ram())
        
        # Scrape Graphics Cards
        self.logger.info("Scraping Graphics Cards...")
        products.extend(self.scrape_graphics_cards())
        
        # Scrape CPUs
        self.logger.info("Scraping CPUs...")
        products.extend(self.scrape_cpus())
        
        self.logger.info(f"Completed scrape for {self.retailer_name}. Found {len(products)} products")
        
        return products
    
    def create_product(self, name: str, price: float, url: str, 
                      category: str, in_stock: bool = True,
                      original_price: Optional[float] = None) -> Product:
        """
        Create a Product object with retailer information.
        
        Args:
            name: Product name
            price: Current price
            url: Product URL
            category: Product category
            in_stock: Stock availability
            original_price: Original price before discount
            
        Returns:
            Product object
        """
        return Product(
            name=name,
            price=price,
            url=url,
            retailer=self.retailer_name,
            category=category,
            in_stock=in_stock,
            original_price=original_price,
            scraped_at=datetime.now()
        )
