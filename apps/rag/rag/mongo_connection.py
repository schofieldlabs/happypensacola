import os
import pymongo
import certifi
import ssl

def get_mongo_client():
    MONGODB_URI = os.getenv("MONGODB_URI")
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable not set.")
    
    client = pymongo.MongoClient(
        MONGODB_URI,
        tls=True,
        tlsAllowInvalidCertificates=False,
        tlsCAFile=certifi.where()
    )

    return client
