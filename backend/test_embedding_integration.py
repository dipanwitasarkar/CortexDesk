import asyncio
from app.services.llm_service import llm_service

async def test_embedding():
    text = "This is a test document for RAG functionality with local embeddings"
    embedding = await llm_service.generate_embedding(text)
    print(f"Embedding length: {len(embedding)}")
    print(f"Embedding type: {type(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    return embedding

if __name__ == "__main__":
    result = asyncio.run(test_embedding())
    print(f"Test completed: {result[:5] if result else 'failed'}")