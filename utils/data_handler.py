"""Utilities for handling and exporting scraped data."""

import json
import os
from datetime import datetime
from typing import List

import pandas as pd

from models.product import Product


def save_products_json(products: List[Product], filename: str = None) -> str:
    """
    Save products to JSON file.
    
    Args:
        products: List of Product objects
        filename: Output filename (optional)
        
    Returns:
        Path to saved file
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'deals_{timestamp}.json'
    
    os.makedirs('output', exist_ok=True)
    filepath = os.path.join('output', filename)
    
    data = [product.to_dict() for product in products]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath


def save_products_csv(products: List[Product], filename: str = None) -> str:
    """
    Save products to CSV file.
    
    Args:
        products: List of Product objects
        filename: Output filename (optional)
        
    Returns:
        Path to saved file
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'deals_{timestamp}.csv'
    
    os.makedirs('output', exist_ok=True)
    filepath = os.path.join('output', filename)
    
    data = [product.to_dict() for product in products]
    df = pd.DataFrame(data)
    
    # Reorder columns for better readability
    column_order = ['retailer', 'category', 'name', 'price', 'original_price', 
                   'discount_percentage', 'savings', 'in_stock', 'url', 'scraped_at']
    
    # Only include columns that exist
    column_order = [col for col in column_order if col in df.columns]
    df = df[column_order]
    
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    return filepath


def get_best_deals(products: List[Product], top_n: int = 10) -> List[Product]:
    """
    Get the best deals based on discount percentage and price.
    
    Args:
        products: List of Product objects
        top_n: Number of top deals to return
        
    Returns:
        List of top Product objects
    """
    # Sort by discount percentage (if available) then by price (lower is better)
    sorted_products = sorted(
        products,
        key=lambda p: (
            -(p.discount_percentage or 0),  # Negative for descending order
            p.price
        )
    )
    
    return sorted_products[:top_n]


def filter_by_category(products: List[Product], category: str) -> List[Product]:
    """Filter products by category."""
    return [p for p in products if p.category == category]


def filter_in_stock(products: List[Product]) -> List[Product]:
    """Filter only in-stock products."""
    return [p for p in products if p.in_stock]


def get_price_statistics(products: List[Product]) -> dict:
    """
    Calculate price statistics for products.
    
    Args:
        products: List of Product objects
        
    Returns:
        Dictionary with statistics
    """
    if not products:
        return {}
    
    prices = [p.price for p in products]
    
    return {
        'min_price': min(prices),
        'max_price': max(prices),
        'avg_price': sum(prices) / len(prices),
        'total_products': len(products)
    }
