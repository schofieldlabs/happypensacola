import os
import fitz
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from apps.rag.mongo_connection import get_mongo_client

DATABASE_NAME = 'rag_db'
COLLECTION_NAME = 'documents'
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

client = get_mongo_client()
collection = client[DATABASE_NAME][COLLECTION_NAME]

faiss_index = faiss.IndexFlatL2(384)
metadata = []

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
        raise ValueError("Unsupported file type.")

def ingest_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        print(f"\nIngesting: {file_path}")
        try:
            text = extract_text(file_path)
            chunks = splitter.split_text(text)
            for chunk in chunks:
                embedding = embedding_model.encode(chunk).astype("float32")
                faiss_index.add(np.array([embedding]))
                metadata.append({"text": chunk, "source_file": filename})
                document = {"text": chunk, "embedding": embedding.tolist(), "source_file": filename}
                collection.insert_one(document)
            print(f"Ingested {len(chunks)} chunks from {filename}.")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    faiss.write_index(faiss_index, "faiss_index.idx")
    with open("metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)

if __name__ == "__main__":
    ingest_directory("docs")
