#!/usr/bin/env python3
"""
PC Deals Scraper - Main Application
Scrapes European retailers for the best deals on DDR5 RAM and Graphics Cards.
"""

import argparse
import logging
from typing import List

from scrapers.amazon_scraper import AmazonScraper
from scrapers.generic_scraper import GenericRetailerScraper
from models.product import Product
from utils.data_handler import (
    save_products_json,
    save_products_csv,
    get_best_deals,
    filter_by_category,
    filter_in_stock,
    get_price_statistics
)
import config


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def scrape_all_retailers(amazon_only: bool = False) -> List[Product]:
    """
    Scrape all configured retailers.
    
    Args:
        amazon_only: If True, only scrape Amazon sites
        
    Returns:
        List of all scraped products
    """
    all_products = []
    
    # Scrape Amazon sites
    logging.info("Starting Amazon scraping...")
    for country in config.AMAZON_COUNTRIES:
        try:
            scraper = AmazonScraper(country_code=country)
            products = scraper.scrape_all()
            all_products.extend(products)
            logging.info(f"Amazon {country.upper()}: Found {len(products)} products")
        except Exception as e:
            logging.error(f"Error scraping Amazon {country.upper()}: {e}")
    
    if not amazon_only:
        # Scrape other European retailers
        logging.info("Starting other retailers scraping...")
        for retailer_id, retailer_config in config.RETAILER_CONFIGS.items():
            try:
                scraper = GenericRetailerScraper(
                    retailer_name=retailer_config['name'],
                    base_url=retailer_config['base_url'],
                    ddr5_search_path=retailer_config['ddr5_search_path'],
                    gpu_search_path=retailer_config['gpu_search_path'],
                    selectors=retailer_config['selectors']
                )
                products = scraper.scrape_all()
                all_products.extend(products)
                logging.info(f"{retailer_config['name']}: Found {len(products)} products")
            except Exception as e:
                logging.error(f"Error scraping {retailer_config['name']}: {e}")
    
    return all_products


def print_summary(products: List[Product]):
    """Print summary of scraped products."""
    print("\n" + "="*80)
    print("SCRAPING SUMMARY")
    print("="*80)
    
    in_stock = filter_in_stock(products)
    print(f"Total products found: {len(products)}")
    print(f"In stock: {len(in_stock)}")
    
    # Category breakdown
    ddr5_products = filter_by_category(products, 'DDR5 RAM')
    gpu_products = filter_by_category(products, 'Graphics Card')
    
    print(f"\nDDR5 RAM: {len(ddr5_products)} products")
    if ddr5_products:
        stats = get_price_statistics(ddr5_products)
        print(f"  Price range: €{stats['min_price']:.2f} - €{stats['max_price']:.2f}")
        print(f"  Average: €{stats['avg_price']:.2f}")
    
    print(f"\nGraphics Cards: {len(gpu_products)} products")
    if gpu_products:
        stats = get_price_statistics(gpu_products)
        print(f"  Price range: €{stats['min_price']:.2f} - €{stats['max_price']:.2f}")
        print(f"  Average: €{stats['avg_price']:.2f}")
    
    # Best deals
    print("\n" + "-"*80)
    print("TOP 5 DEALS")
    print("-"*80)
    
    best_deals = get_best_deals(in_stock, top_n=5)
    for i, product in enumerate(best_deals, 1):
        discount_info = ""
        if product.discount_percentage:
            discount_info = f" (-{product.discount_percentage}%, save €{product.savings:.2f})"
        
        print(f"\n{i}. {product.name[:60]}...")
        print(f"   Retailer: {product.retailer}")
        print(f"   Price: €{product.price:.2f}{discount_info}")
        print(f"   URL: {product.url[:70]}...")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description='Scrape European retailers for PC component deals'
    )
    parser.add_argument(
        '--amazon-only',
        action='store_true',
        help='Only scrape Amazon sites'
    )
    parser.add_argument(
        '--output',
        choices=['json', 'csv', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Skip printing summary'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Start scraping
    logging.info("Starting PC Deals Scraper...")
    products = scrape_all_retailers(amazon_only=args.amazon_only)
    
    if not products:
        logging.warning("No products found!")
        return
    
    # Save results
    if args.output in ['json', 'both']:
        json_path = save_products_json(products)
        logging.info(f"Saved JSON results to: {json_path}")
    
    if args.output in ['csv', 'both']:
        csv_path = save_products_csv(products)
        logging.info(f"Saved CSV results to: {csv_path}")
    
    # Print summary
    if not args.no_summary:
        print_summary(products)
    
    print("\n" + "="*80)
    print("Scraping completed successfully!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
