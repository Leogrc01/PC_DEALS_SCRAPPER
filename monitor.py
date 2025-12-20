#!/usr/bin/env python3
"""
PC Deals Monitor - Continuous monitoring with notifications
Monitors RAM availability and alerts when good deals are in stock.
"""

import argparse
import logging
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Set
import subprocess

from scrapers.amazon_scraper import AmazonScraper
from models.product import Product
from utils.data_handler import filter_by_category, filter_in_stock
import config


class RAMMonitor:
    """Monitor RAM deals and send notifications for good deals."""
    
    def __init__(self, max_price: float = None, check_interval: int = 300, 
                 min_capacity: int = 16, sound_enabled: bool = True):
        """
        Initialize RAM monitor.
        
        Args:
            max_price: Maximum price in EUR (None = no limit)
            check_interval: Seconds between checks (default: 5 minutes)
            min_capacity: Minimum RAM capacity in GB (default: 16GB)
            sound_enabled: Play sound with notification
        """
        self.max_price = max_price
        self.check_interval = check_interval
        self.min_capacity = min_capacity
        self.sound_enabled = sound_enabled
        self.notified_products: Set[str] = set()  # Track already notified products
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create cache directory
        self.cache_dir = Path('cache')
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / 'notified_products.json'
        
        # Load previously notified products
        self._load_notified_cache()
    
    def _load_notified_cache(self):
        """Load previously notified products from cache."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.notified_products = set(data.get('products', []))
                    self.logger.info(f"Loaded {len(self.notified_products)} previously notified products")
            except Exception as e:
                self.logger.warning(f"Could not load cache: {e}")
    
    def _save_notified_cache(self):
        """Save notified products to cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({'products': list(self.notified_products)}, f)
        except Exception as e:
            self.logger.warning(f"Could not save cache: {e}")
    
    def _extract_capacity(self, name: str) -> int:
        """
        Extract total RAM capacity from product name.
        
        Returns capacity in GB, or 0 if not found.
        """
        import re
        name_lower = name.lower()
        
        # Match patterns like: "32GB", "2x16GB", "2 x 16GB", etc.
        patterns = [
            r'(\d+)\s*x\s*(\d+)\s*gb',  # 2x16GB format
            r'(\d+)\s*gb.*?kit',  # Direct capacity with "kit"
            r'(\d+)\s*go',  # French format
            r'(\d+)\s*gb',  # Simple format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name_lower)
            if match:
                if len(match.groups()) == 2:
                    # Format like 2x16GB
                    return int(match.group(1)) * int(match.group(2))
                else:
                    # Direct capacity
                    return int(match.group(1))
        
        return 0
    
    def _should_notify(self, product: Product) -> bool:
        """
        Check if product meets notification criteria.
        
        Returns True if product should trigger notification.
        """
        # Must be in stock
        if not product.in_stock:
            return False
        
        # Check price limit
        if self.max_price and product.price > self.max_price:
            return False
        
        # Check minimum capacity
        capacity = self._extract_capacity(product.name)
        if capacity > 0 and capacity < self.min_capacity:
            return False
        
        # Check if already notified
        product_id = f"{product.retailer}:{product.name}:{product.price}"
        if product_id in self.notified_products:
            return False
        
        return True
    
    def _send_notification(self, product: Product):
        """Send macOS notification for a product."""
        try:
            capacity = self._extract_capacity(product.name)
            capacity_str = f"{capacity}GB " if capacity > 0 else ""
            
            # Truncate name for notification
            short_name = product.name[:60] + "..." if len(product.name) > 60 else product.name
            
            title = f"🎯 RAM Disponible: {capacity_str}€{product.price:.2f}"
            message = f"{short_name}\n{product.retailer}"
            
            # Send macOS notification
            script = f'''
            display notification "{message}" with title "{title}" sound name "{"Glass" if self.sound_enabled else ""}"
            '''
            subprocess.run(['osascript', '-e', script], check=False)
            
            # Also speak it out for maximum attention (optional)
            if self.sound_enabled:
                speak_text = f"RAM disponible à {product.price:.0f} euros"
                subprocess.run(['say', '-v', 'Thomas', speak_text], check=False)
            
            self.logger.info(f"📢 NOTIFICATION: {title}")
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
    
    def _display_console_alert(self, products: List[Product]):
        """Display alert in console with product details."""
        print("\n" + "🚨" * 40)
        print("  " * 10 + "ALERTE RAM DISPONIBLE!")
        print("🚨" * 40 + "\n")
        
        for i, product in enumerate(products, 1):
            capacity = self._extract_capacity(product.name)
            capacity_str = f"[{capacity}GB] " if capacity > 0 else ""
            
            print(f"{i}. {capacity_str}{product.name[:70]}")
            print(f"   💰 Prix: €{product.price:.2f}")
            
            # Display delivery info if available
            if product.delivery_text:
                print(f"   🚚 Livraison: {product.delivery_text}")
            
            print(f"   🏪 Vendeur: {product.retailer}")
            print(f"   🔗 {product.url}")
            print()
        
        print("🚨" * 40 + "\n")
    
    def scan_once(self) -> List[Product]:
        """
        Perform one scan of all Amazon sites.
        
        Returns list of products that meet notification criteria.
        """
        all_ram_products = []
        
        # Scrape all Amazon sites
        for country in config.AMAZON_COUNTRIES:
            try:
                scraper = AmazonScraper(country_code=country)
                products = scraper.scrape_ddr5_ram()
                all_ram_products.extend(products)
                self.logger.debug(f"Amazon {country.upper()}: {len(products)} RAM products")
            except Exception as e:
                self.logger.error(f"Error scraping Amazon {country.upper()}: {e}")
        
        # Filter to in-stock only
        in_stock_products = filter_in_stock(all_ram_products)
        self.logger.info(f"Found {len(in_stock_products)} RAM in stock (out of {len(all_ram_products)} total)")
        
        # Find products that meet notification criteria
        notify_products = []
        for product in in_stock_products:
            if self._should_notify(product):
                notify_products.append(product)
                
                # Mark as notified
                product_id = f"{product.retailer}:{product.name}:{product.price}"
                self.notified_products.add(product_id)
        
        # Sort by delivery date (earliest first), then by price
        notify_products.sort(key=lambda p: (
            p.delivery_date if p.delivery_date else datetime.max,  # Products without date go last
            p.price
        ))
        
        if notify_products:
            self._save_notified_cache()
        
        return notify_products
    
    def monitor_loop(self):
        """Main monitoring loop."""
        self.logger.info("=" * 80)
        self.logger.info("RAM Monitor started")
        self.logger.info(f"Price limit: €{self.max_price:.2f}" if self.max_price else "Price limit: None")
        self.logger.info(f"Min capacity: {self.min_capacity}GB")
        self.logger.info(f"Check interval: {self.check_interval}s ({self.check_interval/60:.1f} min)")
        self.logger.info(f"Sound: {'ON' if self.sound_enabled else 'OFF'}")
        self.logger.info("=" * 80 + "\n")
        
        scan_count = 0
        
        try:
            while True:
                scan_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Clear visual separator for scan start
                print("\n" + "═" * 80)
                self.logger.info(f"🔍 SCAN #{scan_count} - {timestamp}")
                print("═" * 80)
                
                # Perform scan
                notify_products = self.scan_once()
                
                # Scan complete separator
                print("─" * 80)
                
                # Send notifications
                if notify_products:
                    self.logger.info(f"✅ Found {len(notify_products)} new RAM deals!")
                    
                    # Display in console
                    self._display_console_alert(notify_products)
                    
                    # Send system notifications
                    for product in notify_products:
                        self._send_notification(product)
                        time.sleep(1)  # Space out notifications
                else:
                    self.logger.info("😴 No new RAM deals found.")
                
                # Wait before next scan
                self.logger.info(f"⏰ Next scan in {self.check_interval}s ({self.check_interval/60:.1f} min)...")
                print("═" * 80 + "\n")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("\n\n" + "=" * 80)
            self.logger.info(f"Monitor stopped. Total scans: {scan_count}")
            self.logger.info(f"Total products notified: {len(self.notified_products)}")
            self.logger.info("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Monitor RAM deals and notify when good deals are available'
    )
    parser.add_argument(
        '--max-price',
        type=float,
        help='Maximum price in EUR (e.g., 150.00)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Check interval in seconds (default: 300 = 5 minutes)'
    )
    parser.add_argument(
        '--min-capacity',
        type=int,
        default=16,
        help='Minimum RAM capacity in GB (default: 16)'
    )
    parser.add_argument(
        '--no-sound',
        action='store_true',
        help='Disable sound notifications'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--reset-cache',
        action='store_true',
        help='Reset notification cache (re-notify for all products)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Reset cache if requested
    if args.reset_cache:
        cache_file = Path('cache/notified_products.json')
        if cache_file.exists():
            cache_file.unlink()
            print("✅ Notification cache reset")
    
    # Create and start monitor
    monitor = RAMMonitor(
        max_price=args.max_price,
        check_interval=args.interval,
        min_capacity=args.min_capacity,
        sound_enabled=not args.no_sound
    )
    
    monitor.monitor_loop()


if __name__ == '__main__':
    main()
