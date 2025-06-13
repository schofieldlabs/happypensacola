# ingest_documents.py

import os
import pymongo
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# === CONFIGURATION ===

MONGODB_URI = os.getenv("MONGODB_URI")  # set this env var before running
DATABASE_NAME = 'rag_db'
COLLECTION_NAME = 'documents'
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# === INITIALIZE MODELS ===

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # your local embedding model

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

client = pymongo.MongoClient(MONGODB_URI)
collection = client[DATABASE_NAME][COLLECTION_NAME]

# === FUNCTIONS ===

def extract_text(file_path):
    if file_path.lower().endswith(".pdf"):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type. Use PDF or TXT.")

def ingest_file(file_path):
    print(f"\nIngesting file: {file_path}")
    text = extract_text(file_path)
    chunks = splitter.split_text(text)
    for chunk in chunks:
        embedding = embedding_model.encode(chunk).tolist()
        document = {
            "text": chunk,
            "embedding": embedding,
            "source_file": os.path.basename(file_path)
        }
        collection.insert_one(document)
    print(f"Ingested {len(chunks)} chunks from {file_path}.")

# === MAIN ===

if __name__ == "__main__":
    files = [
        "docs/phh3200.pdf"
    ]
    for file_path in files:
        ingest_file(file_path)
