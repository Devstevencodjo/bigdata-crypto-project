import requests
import json
import time
from kafka import KafkaProducer
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Kafka
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_TOPIC = 'crypto-prices'

# Configuration API CoinGecko (gratuite)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

# Configuration des cryptos à surveiller (TOP cryptos vérifiées)
CRYPTOS = [
    "bitcoin", "ethereum", "tether", "ripple", "binancecoin", 
    "solana", "usd-coin", "dogecoin", "cardano", "avalanche-2",
    "shiba-inu", "chainlink", "polkadot", "litecoin", "uniswap", 
    "ethereum-classic", "stellar", "filecoin", "cosmos", "hedera-hashgraph", 
    "cronos", "near", "vechain", "algorand", "the-sandbox", 
    "decentraland", "internet-computer", "apecoin", "theta-token", 
    "flow", "tezos", "enjincoin", "klay-token", "neo", "waves", 
    "zilliqa", "zcash"
]


def create_kafka_producer():
    """Créer un producteur Kafka"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        logger.info("✅ Producteur Kafka créé avec succès")
        return producer
    except Exception as e:
        logger.error(f"❌ Erreur création producteur Kafka: {e}")
        return None

def get_crypto_prices():
    """Récupérer les prix des cryptos depuis CoinGecko"""
    try:
        params = {
            'ids': ','.join(CRYPTOS),
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }

        response = requests.get(COINGECKO_API_URL, params=params)
        response.raise_for_status()

        data = response.json()

        # Ajout temporaire pour détecter les cryptos manquantes
        fetched_ids = set(data.keys())
        expected_ids = set(CRYPTOS)
        missing_ids = expected_ids - fetched_ids

        if missing_ids:
            logger.warning(f"⚠️ Cryptos non retournées par l'API : {missing_ids}")

        logger.info(f"✅ Prix récupérés pour {len(data)} cryptos")
        return data

    except Exception as e:
        logger.error(f"❌ Erreur récupération prix: {e}")
        return None


def format_crypto_data(crypto_id, data):
    """Formater les données crypto avec plus d'infos"""
    return {
        'id': crypto_id,
        'name': crypto_id.replace('-', ' ').title(),
        'price_usd': data['usd'],
        'market_cap': data.get('usd_market_cap', 0),
        'volume_24h': data.get('usd_24h_vol', 0),
        'change_24h': data.get('usd_24h_change', 0),
        'timestamp': datetime.now().isoformat(),
        'price_formatted': f"${data['usd']:,.2f}",
        'change_emoji': "📈" if (data.get('usd_24h_change') or 0) > 0 else "📉",
        'market_cap_b': f"${data.get('usd_market_cap', 0) / 1_000_000_000:.1f}B"
    }

def send_to_kafka(producer, data):
    """Envoyer les données vers Kafka"""
    try:
        for crypto, info in data.items():
            message = format_crypto_data(crypto, info)
            producer.send(KAFKA_TOPIC, key=crypto, value=message)
            logger.info(f"📤 Envoyé: {message['name']} = {message['price_formatted']} {message['change_emoji']}")
        producer.flush()
    except Exception as e:
        logger.error(f"❌ Erreur envoi Kafka: {e}")

def main():
    """Fonction principale"""
    logger.info("🚀 Démarrage du producteur crypto...")

    # Créer le producteur Kafka
    producer = create_kafka_producer()
    if not producer:
        return

    try:
        while True:
            crypto_data = get_crypto_prices()

            if crypto_data:
                send_to_kafka(producer, crypto_data)
                logger.info(f"✅ Données envoyées à {datetime.now()}")
            else:
                logger.warning("⚠️ Aucune donnée récupérée")

            time.sleep(30)

    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du producteur")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
