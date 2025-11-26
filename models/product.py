"""Product data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """Represents a PC component product."""
    
    name: str
    price: float
    url: str
    retailer: str
    category: str
    in_stock: bool = True
    original_price: Optional[float] = None
    scraped_at: datetime = None
    
    @property
    def discount_percentage(self) -> Optional[float]:
        """Calculate discount percentage if original price is available."""
        if self.original_price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100, 2)
        return None
    
    @property
    def savings(self) -> Optional[float]:
        """Calculate savings amount if original price is available."""
        if self.original_price and self.original_price > self.price:
            return round(self.original_price - self.price, 2)
        return None
    
    def to_dict(self) -> dict:
        """Convert product to dictionary."""
        return {
            'name': self.name,
            'price': self.price,
            'url': self.url,
            'retailer': self.retailer,
            'category': self.category,
            'in_stock': self.in_stock,
            'original_price': self.original_price,
            'discount_percentage': self.discount_percentage,
            'savings': self.savings,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }
