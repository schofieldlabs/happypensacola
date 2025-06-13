import numpy as np
import pickle
import faiss
import threading
from sentence_transformers import SentenceTransformer
from langchain_community.chat_models import ChatOllama

# Lazy load globals
embedding_model = None
faiss_index = None
llm = None

# Load metadata at startup (safe - small file)
with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

faiss_lock = threading.Lock()

def load_resources():
    global faiss_index, embedding_model, llm
    with faiss_lock:
        if faiss_index is None:
            faiss_index = faiss.read_index("faiss_index.idx")
        if embedding_model is None:
            embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        if llm is None:
            llm = ChatOllama(model="llama3")

def retrieve_similar_docs(query, top_k=5):
    load_resources()
    query_embedding = embedding_model.encode(query).astype("float32")
    D, I = faiss_index.search(np.array([query_embedding]), top_k)
    return [metadata[i]["text"] for i in I[0]]

def run_rag_pipeline(query):
    context_docs = retrieve_similar_docs(query)
    context = "\n---\n".join(context_docs)
    prompt = f"Answer based on the following:\n\n{context}\n\nQuestion:\n{query}\nAnswer:"
    response = llm.invoke(prompt)
    return response.content
