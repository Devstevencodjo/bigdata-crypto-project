# bigdata-crypto-project
Proxy Big Data centralisant les appels API crypto (CoinGecko) via pipeline Kafka → Elasticsearch → Kibana.


# 🚀 Crypto Tracking Application - Projet Big Data Temps Réel

## 📋 Contexte du Projet

Cette application centralise la récupération des taux de cryptomonnaies pour optimiser les coûts d'API. Au lieu que chaque équipe appelle directement l'API CoinGecko, notre solution :

- ✅ Récupère les données crypto via l'API CoinGecko
- ✅ Publie les données en temps réel sur Kafka
- ✅ Stocke les données dans Elasticsearch
- ✅ Visualise les données via Kibana

Les équipes internes peuvent alors consommer les données depuis Kafka sans accéder directement à l'API externe.

## 🏗️ Architecture

┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ │ │ │ │ │
│ CoinGecko │───▶│ Kafka │───▶│ Elasticsearch │
│ API │ │ (crypto-data) │ │ (crypto-prices)│
│ │ │ │ │ │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│ │
┌─────────────────┐ ┌─────────────────┐
│ │ │ │
│ Producer │ │ Kibana │
│ (crypto_api) │ │ (Dashboards) │
│ │ │ │
└─────────────────┘ └─────────────────┘
│
┌─────────────────┐
│ │
│ Consumer │
│(crypto_consumer)│
│ │
└─────────────────┘


## 📁 Structure du Projet

bigdata-crypto-project/
│
├── README.md # Documentation du projet
├── requirements.txt # Dépendances Python
├── .gitignore # Fichiers à ignorer
│
├── src/
│ ├── crypto_api.py # Producer Kafka - Récupération API
│ ├── crypto_consumer.py # Consumer Kafka - Indexation ES
│ └── config.py # Configuration centralisée
│
├── docker/
│ └── docker-compose.yml # Stack ELK + Kafka
│
├── docs/
│ ├── installation.md # Guide d'installation
│ └── screenshots/ # Captures d'écran
│
└── scripts/
├── start_services.sh # Démarrage des services
├── create_topics.sh # Création topics Kafka
└── setup_kibana.sh # Configuration Kibana


## 🛠️ Technologies Utilisées

| Technologie | Version | Rôle |
|-------------|---------|------|
| **Python** | 3.9+ | Développement application |
| **Apache Kafka** | 2.8.0 | Message broker temps réel |
| **Elasticsearch** | 8.11.0 | Base de données NoSQL |
| **Kibana** | 8.11.0 | Visualisation des données |
| **Docker** | - | Conteneurisation |

## 📦 Dépendances Python

```txt
kafka-python==2.0.2
elasticsearch==8.11.0
requests==2.31.0
python-dotenv==1.0.0
schedule==1.2.0

⚙️ Installation et Configuration
1. Prérequis
# Installer Python 3.9+
# Installer Docker et Docker Compose
# Vérifier les ports disponibles : 9092, 9200, 5601

2. Cloner le Projet
git clone https://github.com/votre-username/bigdata-crypto-project.git
cd bigdata-crypto-project

3. Environnement Virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

4. Installer les Dépendances
pip install -r requirements.txt

5. Démarrer les Services
# Démarrer Kafka
cd /opt/homebrew/bin
./kafka-server-start /opt/homebrew/etc/kafka/server.properties

# Nouveau terminal - Démarrer Elasticsearch
elasticsearch

# Nouveau terminal - Démarrer Kibana
kibana

6. Créer le Topic Kafka
kafka-topics --create --topic crypto-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

🚀 Utilisation
Démarrage de l'Application
1. Lancer le Producer (Terminal 1)
cd bigdata-crypto-project
source venv/bin/activate
python crypto_api.py

Résultat attendu :

🚀 Démarrage récupération crypto toutes les 60 secondes...
📊 Récupération données - 14:38:04
✅ Envoyé: Bitcoin - $105330
✅ Envoyé: Ethereum - $2624.06
✅ 50 cryptos envoyées vers Kafka
⏳ Attente 60 secondes...

2. Lancer le Consumer (Terminal 2)
cd bigdata-crypto-project
source venv/bin/activate
python crypto_consumer.py

Résultat attendu :

🚀 Consumer Kafka démarré, en attente de messages...
📊 Traitement: Bitcoin - $105330.0 - 2025-01-07 14:38:04
✅ Données envoyées vers Elasticsearch

3. Vérifier l'Indexation
curl "localhost:9200/_cat/indices?v"

Résultat attendu :

health status index         docs.count store.size
yellow open   crypto-prices        87     42.9kb

Accès aux Interfaces
Service	URL	Description
Kibana	http://localhost:5601	Dashboards et visualisations
Elasticsearch	http://localhost:9200	API REST pour les données
📊 Configuration Kibana
1. Créer un Data View
Ouvrir Kibana : http://localhost:5601
Menu → Stack Management → Data Views
Create data view
Name : crypto-prices
Index pattern : crypto-prices
Timestamp field : timestamp
2. Dashboards Recommandés
📈 Prix en Temps Réel
Type : Line chart
X-axis : timestamp
Y-axis : price
Split series : symbol
🏆 Top 10 Cryptos
Type : Horizontal bar
Y-axis : symbol
X-axis : Average of price
📋 Tableau de Données
Type : Data table
Colonnes : name, symbol, price, market_cap
📈 Données Collectées
Structure des Documents Elasticsearch
{
  "_index": "crypto-prices",
  "_source": {
    "symbol": "BTC",
    "name": "Bitcoin",
    "price": 105330.0,
    "market_cap": 2084329845234,
    "volume_24h": 28456789123,
    "change_24h": 2.45,
    "timestamp": "2025-01-07T14:38:04.123456"
  }
}

Fréquence de Collecte
⏱️ Intervalle : 60 secondes
📊 Cryptos suivies : Top 50 par market cap
🔄 Mode : Temps réel continu
🧪 Tests et Validation
Vérification du Pipeline
1. Test Producer
# Vérifier les messages Kafka
kafka-console-consumer --bootstrap-server localhost:9092 --topic crypto-data --from-beginning

2. Test Elasticsearch
# Compter les documents
curl "localhost:9200/crypto-prices/_count"

# Voir un échantillon
curl "localhost:9200/crypto-prices/_search?size=5" | jq

3. Test Consumer
# Logs attendus
tail -f consumer.log

🚨 Dépannage
Problèmes Fréquents
Kafka ne démarre pas
# Vérifier le port 9092
netstat -an | grep 9092

# Nettoyer les logs Kafka
rm -rf /opt/homebrew/var/lib/kafka-logs/*

Elasticsearch inaccessible
# Vérifier le status
curl localhost:9200/_cluster/health

# Redémarrer si nécessaire
brew services restart elasticsearch

Pas de données dans Kibana
# Vérifier l'index
curl "localhost:9200/crypto-prices/_search?size=1"

# Recréer le data view si besoin

Messages d'Erreur Courants
Erreur	Solution
Connection refused 9092	Démarrer Kafka
Index not found	Vérifier le consumer
No data view	Créer le data view dans Kibana

👨‍💻 Développeur
Nom : Steven CODJO
Projet : Application Big Data Temps Réel
Date : Janvier 2025

📝 Licence
Ce projet est développé dans le cadre d'un exercice académique.

🎯 Commandes de Démarrage Rapide
# Terminal 1 - Producer
cd bigdata-crypto-project && source venv/bin/activate && python crypto_api.py

# Terminal 2 - Consumer  
cd bigdata-crypto-project && source venv/bin/activate && python crypto_consumer.py

# Terminal 3 - Monitoring
watch -n 5 'curl -s "localhost:9200/crypto-prices/_count" | jq'
