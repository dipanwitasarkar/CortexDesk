from sentence_transformers import SentenceTransformer
import numpy as np

# Test embedding generation
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
text = "This is a test document for RAG functionality with local embeddings"

# Generate embedding
embedding = model.encode(text, convert_to_numpy=True)
print(f"Embedding shape: {embedding.shape}")
print(f"Embedding type: {type(embedding)}")
print(f"First 5 values: {embedding[:5]}")
print(f"Embedding as list: {embedding.tolist()[:5]}")