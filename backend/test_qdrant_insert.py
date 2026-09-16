from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize Qdrant client
client = QdrantClient(url="http://localhost:6333")

# Initialize embedding model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Test text
text = "This is a test document for RAG functionality with local embeddings"

# Generate embedding
embedding = model.encode(text, convert_to_numpy=True)
embedding_list = embedding.tolist()

print(f"Embedding shape: {embedding.shape}")
print(f"Embedding type: {type(embedding)}")
print(f"Embedding list type: {type(embedding_list)}")
print(f"First 5 values: {embedding_list[:5]}")

# Delete existing collection if it exists
try:
    client.delete_collection("test_collection")
except:
    pass

# Create collection with 384 dimensions
client.create_collection(
    collection_name="test_collection",
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)

print("Collection created")

# Try different insertion methods

# Method 1: Using PointStruct with list
try:
    point = PointStruct(
        id=1,
        vector=embedding_list,
        payload={"text": text}
    )
    client.upsert(
        collection_name="test_collection",
        points=[point]
    )
    print("Method 1 (PointStruct with list): SUCCESS")
except Exception as e:
    print(f"Method 1 (PointStruct with list): FAILED - {e}")

# Method 2: Using PointStruct with numpy array
try:
    point = PointStruct(
        id=2,
        vector=embedding,
        payload={"text": text}
    )
    client.upsert(
        collection_name="test_collection",
        points=[point]
    )
    print("Method 2 (PointStruct with numpy): SUCCESS")
except Exception as e:
    print(f"Method 2 (PointStruct with numpy): FAILED - {e}")

# Method 3: Using direct dict
try:
    client.upsert(
        collection_name="test_collection",
        points=[{
            "id": 3,
            "vector": embedding_list,
            "payload": {"text": text}
        }]
    )
    print("Method 3 (direct dict): SUCCESS")
except Exception as e:
    print(f"Method 3 (direct dict): FAILED - {e}")

# Method 4: Using insert_points method
try:
    from qdrant_client.models import PointStruct
    points = [
        PointStruct(
            id=4,
            vector=embedding_list,
            payload={"text": text}
        )
    ]
    client.upsert(
        collection_name="test_collection",
        points=points
    )
    print("Method 4 (insert_points style): SUCCESS")
except Exception as e:
    print(f"Method 4 (insert_points style): FAILED - {e}")

# Check collection info
try:
    info = client.get_collection("test_collection")
    print(f"Collection info: {info.points_count} points")
except Exception as e:
    print(f"Get collection info: FAILED - {e}")

# Clean up
try:
    client.delete_collection("test_collection")
    print("Collection deleted")
except:
    pass