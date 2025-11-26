"""Utilities for handling and exporting scraped data."""

import json
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

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

# ---------- Grouping & Reporting ----------

def _categorize_gpu(name: str) -> str:
    """Return a GPU category like 'RTX 3060 8G', 'RTX 4070 Ti 12G', 'RX 7600 8G', etc."""
    s = name.lower()
    model = None
    
    # NVIDIA RTX - extract exact model (e.g., 3060, 3070, 4060 Ti, 4070 Super)
    # Pattern: RTX [3/4/5]0[0-9][0-9] [optional Ti/Super/etc]
    m_rtx = re.search(r"rtx\s*([345]0\d{2})\s*(ti|super|ti super)?", s)
    if m_rtx:
        base = m_rtx.group(1)
        suffix = m_rtx.group(2)
        if suffix:
            model = f"RTX {base} {suffix.title()}"
        else:
            model = f"RTX {base}"
    
    # AMD Radeon RX - extract exact model (e.g., RX 6600, RX 7900 XT)
    if not model:
        m_rx = re.search(r"r[xa]\s*([679]\d{3})\s*(xt|gre)?", s)
        if m_rx:
            base = m_rx.group(1)
            suffix = m_rx.group(2)
            if suffix:
                model = f"RX {base} {suffix.upper()}"
            else:
                model = f"RX {base}"
    
    # Extract VRAM
    vram = None
    m_vram = re.search(r"(\d{1,2})\s?(?:gb|g)\b", s)
    if m_vram:
        try:
            n = int(m_vram.group(1))
            if 1 <= n <= 48:
                vram = f"{n}GB"
        except ValueError:
            pass
    
    if model and vram:
        return f"{model} {vram}"
    if model:
        return f"{model}"
    return "Other"

def _categorize_ram(name: str) -> str:
    """Return a RAM capacity category like '16GB', '32GB', etc."""
    s = name.lower()
    # Pattern like 2x16GB or 2 x 16 GB
    m = re.search(r"(\d+)\s*[x×]\s*(\d+)\s*gb", s)
    if m:
        try:
            total = int(m.group(1)) * int(m.group(2))
            return f"{total}GB"
        except ValueError:
            pass
    # Fallback: first GB mention
    m2 = re.search(r"(\d{1,3})\s*gb", s)
    if m2:
        try:
            total = int(m2.group(1))
            return f"{total}GB"
        except ValueError:
            pass
    return "Other"

def generate_markdown_report(products: List[Product], filename: str | None = None) -> str:
    """
    Generate a grouped Markdown report for GPUs and RAM, sorted by price asc.
    
    Groups:
    - GPUs: by series and VRAM (e.g., 'RTX 30xx 8G')
    - RAM: by total capacity (e.g., '32GB')
    """
    if filename is None:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'grouped_deals_{ts}.md'
    
    os.makedirs('output', exist_ok=True)
    path = os.path.join('output', filename)
    
    # Partition products
    gpus = [p for p in products if p.category == 'Graphics Card']
    rams = [p for p in products if p.category == 'DDR5 RAM']
    
    # Build groups
    gpu_groups: Dict[str, List[Product]] = defaultdict(list)
    for p in gpus:
        gpu_groups[_categorize_gpu(p.name)].append(p)
    
    ram_groups: Dict[str, List[Product]] = defaultdict(list)
    for p in rams:
        ram_groups[_categorize_ram(p.name)].append(p)
    
    # Sort items within groups by price
    for grp in gpu_groups.values():
        grp.sort(key=lambda x: x.price)
    for grp in ram_groups.values():
        grp.sort(key=lambda x: x.price)
    
    # Order groups nicely
    def _gpu_group_key(k: str) -> Tuple[int, int, int]:
        # Order by generation (3xxx < 4xxx < 5xxx < 6xxx < 7xxx < 9xxx), then model number, then VRAM
        generation = 999
        model_num = 999
        vram = 999
        
        # Extract generation and model number
        m = re.search(r"RTX (\d)(\d{3})", k)
        if m:
            generation = int(m.group(1))  # 3, 4, or 5
            model_num = int(m.group(2))   # 060, 070, 080, 090
        else:
            # AMD RX
            m2 = re.search(r"RX ([679])(\d{3})", k)
            if m2:
                generation = int(m2.group(1)) + 10  # 16, 17, 19 to sort after NVIDIA
                model_num = int(m2.group(2))
        
        # Extract VRAM
        m_vram = re.search(r"(\d+)GB", k)
        if m_vram:
            try:
                vram = int(m_vram.group(1))
            except ValueError:
                pass
        
        return (generation, model_num, vram)
    
    def _ram_group_key(k: str) -> int:
        m = re.match(r"(\d+)GB$", k)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                pass
        return 9999
    
    sorted_gpu_groups = sorted(gpu_groups.items(), key=lambda kv: _gpu_group_key(kv[0]))
    sorted_ram_groups = sorted(ram_groups.items(), key=lambda kv: _ram_group_key(kv[0]))
    
    # Render markdown
    lines: List[str] = []
    lines.append(f"# Grouped Deals Report\n")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("")
    
    # GPUs first per user's example
    lines.append("## Graphics Cards\n")
    if not sorted_gpu_groups:
        lines.append("No graphics cards found.\n")
    else:
        for group_name, items in sorted_gpu_groups:
            lines.append(f"### {group_name}\n")
            if not items:
                lines.append("(none)\n")
            else:
                for p in items:
                    price_info = f"€{p.price:.2f}"
                    if p.original_price and p.discount_percentage:
                        price_info = f"~~€{p.original_price:.2f}~~ **€{p.price:.2f}** (-{p.discount_percentage}%)"
                    lines.append(f"- {price_info} — {p.name} ({p.retailer}) — {p.url}")
            lines.append("")
    
    # RAM
    lines.append("## DDR5 RAM\n")
    if not sorted_ram_groups:
        lines.append("No DDR5 RAM found.\n")
    else:
        for group_name, items in sorted_ram_groups:
            lines.append(f"### {group_name}\n")
            if not items:
                lines.append("(none)\n")
            else:
                for p in items:
                    price_info = f"€{p.price:.2f}"
                    if p.original_price and p.discount_percentage:
                        price_info = f"~~€{p.original_price:.2f}~~ **€{p.price:.2f}** (-{p.discount_percentage}%)"
                    lines.append(f"- {price_info} — {p.name} ({p.retailer}) — {p.url}")
            lines.append("")
    
    content = "\n".join(lines) + "\n"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path
