#!/bin/bash
# Script simplifié pour lancer le scraper PC Deals

# Active l'environnement virtuel
source venv/bin/activate

# Afficher le menu
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "                        🛒 PC DEALS SCRAPER MENU 🛒"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "1. 📊 Scrape unique (avec rapport groupé et top deals)"
echo "2. 🔔 Mode monitoring (alertes RAM en temps réel)"
echo "3. ❌ Quitter"
echo ""
read -p "Choisis une option (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Lancement du scrape unique..."
        echo "═══════════════════════════════════════════════════════════════════════════════"
        echo ""
        
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
        
        echo "📄 Pour voir le rapport complet trié, ouvre: output/grouped_deals_*.md"
        echo ""
        ;;
    
    2)
        echo ""
        echo "🔔 Configuration du monitoring..."
        echo "═══════════════════════════════════════════════════════════════════════════════"
        echo ""
        
        # Demander les paramètres
        read -p "💰 Prix maximum en € (laisse vide pour aucune limite): " max_price
        read -p "⏰ Intervalle en secondes (défaut: 300 = 5 min): " interval
        read -p "📦 Capacité minimum en GB (défaut: 16): " min_capacity
        read -p "🔇 Désactiver le son? (y/N): " no_sound
        
        # Construire la commande
        cmd="python monitor.py"
        
        if [ -n "$max_price" ]; then
            cmd="$cmd --max-price $max_price"
        fi
        
        if [ -n "$interval" ]; then
            cmd="$cmd --interval $interval"
        fi
        
        if [ -n "$min_capacity" ]; then
            cmd="$cmd --min-capacity $min_capacity"
        fi
        
        if [ "$no_sound" = "y" ] || [ "$no_sound" = "Y" ]; then
            cmd="$cmd --no-sound"
        fi
        
        echo ""
        echo "🚀 Démarrage du monitoring..."
        echo "💡 Appuie sur Ctrl+C pour arrêter"
        echo "═══════════════════════════════════════════════════════════════════════════════"
        echo ""
        
        # Lancer le monitoring
        $cmd
        ;;
    
    3)
        echo ""
        echo "👋 À bientôt!"
        echo ""
        exit 0
        ;;
    
    *)
        echo ""
        echo "❌ Option invalide. Relance le script."
        echo ""
        exit 1
        ;;
esac
