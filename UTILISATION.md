# Guide d'utilisation rapide

## 🚀 Lancer le scraper

```bash
./scrape.sh
```

C'est tout! Le script va:
1. Activer l'environnement Python
2. Scraper Amazon Europe (DE, FR, ES, IT, UK)
3. Générer 3 fichiers dans `output/`:
   - `deals_YYYYMMDD_HHMMSS.json` - Données brutes JSON
   - `deals_YYYYMMDD_HHMMSS.csv` - Pour Excel
   - `grouped_deals_YYYYMMDD_HHMMSS.md` - **Rapport trié par modèle** ⭐

## 📊 Le rapport Markdown (recommandé)

Ouvre le fichier `grouped_deals_*.md` pour voir:

### Graphics Cards - Triées par modèle exact
- **RTX 3050 8GB**
- **RTX 4060 8GB**
- **RTX 4060 Ti 8GB**
- **RTX 4070 Super 12GB**
- **RX 7600 8GB**
- etc.

### DDR5 RAM - Triées par capacité
- **16GB**
- **32GB**
- **64GB**
- etc.

## 💰 Affichage des prix

- **Prix normal**: €499.99
- **Avec réduction**: ~~€599.99~~ **€499.99** (-16.7%)

Les réductions s'affichent automatiquement quand Amazon les propose!

## 🔧 Installation (première fois uniquement)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 Notes

- Le scraping prend environ 30 secondes
- ~80-90 produits trouvés par exécution
- Les accessoires (supports, câbles, etc.) sont automatiquement filtrés
- Les RAM laptop (SODIMM) sont exclues
