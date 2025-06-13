import numpy as np
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from langchain_community.chat_models import ChatOllama

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
llm = ChatOllama(model="llama3")

faiss_index = faiss.read_index("faiss_index.idx")
with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

def retrieve_similar_docs(query, top_k=5):
    query_embedding = embedding_model.encode(query).astype("float32")
    D, I = faiss_index.search(np.array([query_embedding]), top_k)
    return [metadata[i]["text"] for i in I[0]]

def run_rag_pipeline(query):
    context_docs = retrieve_similar_docs(query)
    context = "\n---\n".join(context_docs)
    prompt = f"Answer based on the following:\n\n{context}\n\nQuestion:\n{query}\nAnswer:"
    response = llm.invoke(prompt)
    return response.content
