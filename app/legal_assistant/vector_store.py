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

'''
Implement caching for vector index
This improves performance by avoiding reloading 
and re-encoding the 545 Q&A on every request.
'''

# Global cache
_index = None
_data = None

def load_data():
    path = os.path.join(os.path.dirname(__file__), "data", "legal_qa.json")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


'''
Right now, every search() call builds the index anew, 
which is slow.
You can cache the index in a global variable 
when the app starts, like:
'''

#This way, the index builds only once per app run.

def create_index():
    global _index, _data
    if _index is not None and _data is not None:
        return _index, _data

    _data = load_data()
    texts = [f"Q: {item['question']}\nA: {item['answer']}" for item in _data]
    vectors = model.encode(texts, convert_to_numpy=True)
    _index = faiss.IndexFlatL2(vectors.shape[1])
    _index.add(vectors)

    return _index, _data

def search(query, top_k=1):
    index, data = create_index()
    query_vec = model.encode([query], convert_to_numpy=True)
    _, indices = index.search(query_vec, top_k)
    return [f"Q: {data[i]['question']}\nA: {data[i]['answer']}" for i in indices[0]]

'''
query is turned into a vector
FAISS searches for top K closest vectors using cosine distance
indices[0] holds the matched vector(s)
You return the original "context" from those matches
This is your R in RAG (Retrieve).
'''
'''
load_data() loads your full QA JSON file 
(make sure the relative path is correct)
create_index() builds the FAISS index on combined Q&A text 
so search considers both question and answer
search() returns the best matched Q&A chunk(s) 
as context strings for your RAG prompt
'''