# app/legal_assistant/vector_store.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os

# "all-MiniLM-L6-v2"
#the name of the pre-trained embedding model
# It takes sentences → dense vectors 
# (like 384 or 768 dimensions) used to calculate similarity.
#"MiniLM-L6" → 6-layer transformer
#"v2" → Version 2 (improved training)

model = SentenceTransformer("all-MiniLM-L6-v2")

def load_data():
    path = os.path.join(os.path.dirname(__file__), "sample_data.json")
    with open(path, "r") as file:
        return json.load(file)

def create_index():
    data = load_data()
    texts = [item["context"] for item in data]
    vectors = model.encode(texts)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(np.array(vectors))
    return index, data

def search(query, top_k=1):
    index, data = create_index()
    query_vec = model.encode([query])
    _, indices = index.search(np.array(query_vec), top_k)
    return [data[i]["context"] for i in indices[0]]
'''
query is turned into a vector
FAISS searches for top K closest vectors using cosine distance
indices[0] holds the matched vector(s)
You return the original "context" from those matches
This is your R in RAG (Retrieve).
'''
