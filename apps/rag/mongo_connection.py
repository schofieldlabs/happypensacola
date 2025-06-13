import os
import pymongo
import certifi
import ssl

def get_mongo_client():
    MONGODB_URI = os.getenv("MONGODB_URI")
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable not set.")
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    client = pymongo.MongoClient(
        MONGODB_URI,
        ssl=True,
        ssl_cert_reqs=ssl.CERT_REQUIRED,
        ssl_ca_certs=certifi.where(),
        ssl_match_hostname=True,
        ssl_context=ssl_context
    )
    return client
