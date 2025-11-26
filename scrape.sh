#!/bin/bash
# Script simplifié pour lancer le scraper PC Deals

# Active l'environnement virtuel
source venv/bin/activate

# Lance le scraper avec toutes les options recommandées
python main.py --amazon-only --grouped-report

echo ""
echo "✅ Scraping terminé!"
echo "📂 Fichiers générés dans: output/"
echo ""

# Afficher le top 5 des meilleurs deals
python << 'EOF'
import json
import glob

files = sorted(glob.glob('output/deals_*.json'))
if files:
    with open(files[-1]) as f:
        data = json.load(f)
    
    deals = [p for p in data if p.get('discount_percentage')]
    
    if deals:
        print("💰 TOP 5 MEILLEURS DEALS:")
        print("="*70)
        
        top_deals = sorted(deals, key=lambda x: x['discount_percentage'], reverse=True)[:5]
        for i, p in enumerate(top_deals, 1):
            name = p['name'][:50]
            orig = p['original_price']
            curr = p['price']
            disc = p['discount_percentage']
            print(f"{i}. {name}...")
            print(f"   €{orig:.2f} → €{curr:.2f} (-{disc}%)")
        print()
    else:
        print("ℹ️  Aucune réduction trouvée pour le moment")
        print()
EOF

echo "Pour voir le rapport complet trié, ouvre: output/grouped_deals_*.md"
