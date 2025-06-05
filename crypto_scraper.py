import requests
import json
from kafka import KafkaProducer
import time
from datetime import datetime

# Configuration Kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def get_crypto_data():
    """Récupère les données crypto depuis CoinGecko"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 50,
        'page': 1,
        'sparkline': 'false'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erreur API: {e}")
        return None

def send_to_kafka(crypto_data):
    """Envoie les données vers Kafka"""
    if not crypto_data:
        return
    
    timestamp = datetime.utcnow().isoformat()
    
    for crypto in crypto_data:
        message = {
            'timestamp': timestamp,
            'id': crypto.get('id'),
            'symbol': crypto.get('symbol'),
            'name': crypto.get('name'),
            'price_usd': crypto.get('current_price'),
            'market_cap': crypto.get('market_cap'),
            'change_24h': crypto.get('price_change_percentage_24h'),
            'volume_24h': crypto.get('total_volume'),
            'rank': crypto.get('market_cap_rank')
        }
        
        try:
            producer.send('crypto-prices', message)
            print(f"✅ Envoyé: {crypto.get('name')} - ${crypto.get('current_price')}")
        except Exception as e:
            print(f"❌ Erreur Kafka: {e}")

def main():
    """Fonction principale"""
    print("🚀 Démarrage du scraper crypto...")
    
    while True:
        try:
            print(f"\n📊 Récupération données - {datetime.now().strftime('%H:%M:%S')}")
            crypto_data = get_crypto_data()
            
            if crypto_data:
                send_to_kafka(crypto_data)
                print(f"✅ {len(crypto_data)} cryptos envoyées vers Kafka")
            else:
                print("❌ Aucune donnée récupérée")
            
            print("⏳ Attente 60 secondes...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du scraper...")
            break
        except Exception as e:
            print(f"❌ Erreur générale: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
