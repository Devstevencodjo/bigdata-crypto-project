# import json
# import time
# from kafka import KafkaConsumer
# from elasticsearch import Elasticsearch
# from datetime import datetime
# import logging

# # Configuration du logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Configuration Kafka
# KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
# KAFKA_TOPIC = 'crypto-prices'

# # Configuration Elasticsearch
# ES_HOST = 'localhost:9200'
# ES_INDEX = 'crypto-prices'

# def create_elasticsearch_client():
#     """Créer le client Elasticsearch"""
#     try:
#         es = Elasticsearch(
#             [f"http://{ES_HOST}"],
#             verify_certs=False,
#             basic_auth=None,
#             request_timeout=30
#         )
        
#         # Tester la connexion
#         if es.ping():
#             logger.info("✅ Connexion Elasticsearch établie")
#             return es
#         else:
#             logger.error("❌ Impossible de se connecter à Elasticsearch")
#             return None
#     except Exception as e:
#         logger.error(f"❌ Erreur Elasticsearch: {e}")
#         return None


# def create_index_mapping(es):
#     """Créer l'index avec mapping optimisé"""
#     mapping = {
#         "mappings": {
#             "properties": {
#                 "crypto_id": {"type": "keyword"},
#                 "name": {"type": "text"},
#                 "symbol": {"type": "keyword"},
#                 "price_usd": {"type": "float"},
#                 "price_formatted": {"type": "keyword"},
#                 "market_cap_usd": {"type": "long"},
#                 "market_cap_formatted": {"type": "keyword"},
#                 "volume_24h": {"type": "long"},
#                 "price_change_24h": {"type": "float"},
#                 "trend": {"type": "keyword"},
#                 "timestamp": {"type": "date"},
#                 "@timestamp": {"type": "date"}
#             }
#         }
#     }
    
#     try:
#         if es.indices.exists(index=ES_INDEX):
#             logger.info(f"📊 Index '{ES_INDEX}' existe déjà")
#         else:
#             es.indices.create(index=ES_INDEX, body=mapping)
#             logger.info(f"🎯 Index '{ES_INDEX}' créé avec succès")
#     except Exception as e:
#         logger.error(f"❌ Erreur création index: {e}")

# def process_message(es, message):
#     """Traiter et indexer un message"""
#     try:
#         # Parser le JSON
#         data = json.loads(message.value.decode('utf-8'))
        
#         # Ajouter timestamp Elasticsearch
#         data['@timestamp'] = datetime.utcnow().isoformat()
        
#         # Indexer dans Elasticsearch
#         doc_id = f"{data['crypto_id']}_{int(time.time())}"
        
#         es.index(
#             index=ES_INDEX,
#             id=doc_id,
#             body=data
#         )
        
#         logger.info(f"📈 Indexé: {data['name']} = {data['price_formatted']} {data['trend']}")
        
#     except Exception as e:
#         logger.error(f"❌ Erreur traitement message: {e}")

# def main():
#     """Fonction principale"""
#     logger.info("🚀 Démarrage du consumer Elasticsearch...")
    
#     # Créer le client Elasticsearch
#     es = create_elasticsearch_client()
#     if not es:
#         return
    
#     # Créer l'index
#     create_index_mapping(es)
    
#     # Créer le consumer Kafka
#     try:
#         consumer = KafkaConsumer(
#             KAFKA_TOPIC,
#             bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#             value_deserializer=lambda x: x,
#             auto_offset_reset='latest',  # Lire seulement les nouveaux messages
#             group_id='crypto-elasticsearch-consumer'
#         )
        
#         logger.info("✅ Consumer Kafka créé avec succès")
#         logger.info("⏳ En attente des messages...")
        
#         # Consommer les messages
#         for message in consumer:
#             process_message(es, message)
            
#     except KeyboardInterrupt:
#         logger.info("🛑 Arrêt du consumer")
#     except Exception as e:
#         logger.error(f"❌ Erreur consumer: {e}")
#     finally:
#         try:
#             consumer.close()
#         except:
#             pass

# if __name__ == "__main__":
#     main()
import json
import time
from kafka import KafkaConsumer
import requests
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Kafka
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_TOPIC = 'crypto-prices'

def test_elasticsearch():
    """Tester Elasticsearch avec requests"""
    try:
        response = requests.get('http://localhost:9200/')
        if response.status_code == 200:
            logger.info("✅ Elasticsearch accessible via HTTP")
            return True
        else:
            logger.error(f"❌ Elasticsearch erreur: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur connexion: {e}")
        return False

def store_in_elasticsearch(data):
    """Stocker directement via API REST"""
    try:
        url = f"http://localhost:9200/crypto-prices/_doc"
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code in [200, 201]:
            # Utiliser get() pour éviter les erreurs de clés manquantes
            name = data.get('name', 'Unknown')
            price = data.get('price_formatted', 'N/A')
            trend = data.get('trend', '')
            
            logger.info(f"📈 Stocké: {name} = {price} {trend}")
            return True
        else:
            logger.error(f"❌ Erreur stockage: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

def process_message(message):
    """Traiter un message Kafka"""
    try:
        # Décoder le message JSON
        data = json.loads(message.value.decode('utf-8'))
        
        # Ajouter timestamp
        data['indexed_at'] = datetime.now().isoformat()
        
        # Stocker dans Elasticsearch
        store_in_elasticsearch(data)
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement: {e}")

def main():
    """Fonction principale"""
    logger.info("🚀 Démarrage du consumer...")
    
    # Tester Elasticsearch
    if not test_elasticsearch():
        logger.error("❌ Elasticsearch non accessible")
        return
    
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: x,
            auto_offset_reset='latest',
            group_id='crypto-elasticsearch-consumer'
        )
        
        logger.info("✅ Consumer Kafka créé")
        logger.info("⏳ En attente des messages...")
        
        for message in consumer:
            process_message(message)
            
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du consumer")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")

if __name__ == "__main__":
    from datetime import datetime
    main()
