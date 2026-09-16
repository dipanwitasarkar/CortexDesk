from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.core.config import settings
from typing import List, Dict, Any, Optional
import uuid
import logging
import httpx

logger = logging.getLogger(__name__)


class QdrantManager:
    def __init__(self):
        self.client: Optional[QdrantClient] = None

    def connect(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None
        )

    async def create_collection(self, collection_name: str, vector_size: int = 384):
        if not self.client:
            self.connect()
        
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if collection_name not in collection_names:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )

    async def insert_points(
        self,
        collection_name: str,
        points: List[Dict[str, Any]]
    ):
        if not self.client:
            self.connect()
        
        try:
            # Convert to Qdrant format
            qdrant_points = []
            for point in points:
                logger.info(f"Processing point: id={point.get('id')}, vector_type={type(point.get('vector'))}, vector_len={len(point.get('vector', []))}")
                qdrant_points.append(
                    PointStruct(
                        id=point.get("id", str(uuid.uuid4())),
                        vector=point["vector"],
                        payload=point.get("payload", {})
                    )
                )
            
            logger.info(f"About to insert {len(qdrant_points)} points into {collection_name}")
            
            # Try using the direct client upsert
            self.client.upsert(
                collection_name=collection_name,
                points=qdrant_points
            )
            logger.info(f"Successfully inserted {len(qdrant_points)} points into {collection_name}")
        except Exception as e:
            logger.error(f"Failed to insert points into Qdrant: {e}")
            logger.error(f"Vector type: {type(points[0]['vector']) if points else 'none'}")
            logger.error(f"Vector length: {len(points[0]['vector']) if points else 'none'}")
            logger.error(f"Vector first 5 values: {points[0]['vector'][:5] if points else 'none'}")
            
            # Fallback: Try using HTTP API directly with correct format
            try:
                logger.info("Attempting fallback using HTTP API directly")
                async with httpx.AsyncClient() as client:
                    url = f"{settings.qdrant_url}/collections/{collection_name}/points"
                    # Use the correct Qdrant REST API format with integer IDs
                    import hashlib
                    payload = {
                        "points": [
                            {
                                "id": int(hashlib.md5(point["id"].encode()).hexdigest()[:8], 16),  # Convert string ID to integer
                                "vector": point["vector"],
                                "payload": point["payload"]
                            }
                            for point in points
                        ]
                    }
                    logger.info(f"HTTP API payload: {payload}")
                    response = await client.put(url, json=payload)
                    logger.info(f"HTTP API response status: {response.status_code}")
                    logger.info(f"HTTP API response body: {response.text}")
                    response.raise_for_status()
                    logger.info(f"Successfully inserted {len(points)} points using HTTP API fallback")
            except Exception as fallback_error:
                logger.error(f"HTTP API fallback also failed: {fallback_error}")
                raise

    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not self.client:
            self.connect()
        
        search_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            search_filter = Filter(must=conditions)
        
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=search_filter
        )
        
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in results
        ]

    async def delete_points(self, collection_name: str, point_ids: List[str]):
        if not self.client:
            self.connect()
        
        # Convert string IDs to integer IDs using the same logic as insert_points
        import hashlib
        integer_ids = [int(hashlib.md5(point_id.encode()).hexdigest()[:8], 16) for point_id in point_ids]
        
        logger.info(f"Deleting points from {collection_name}: {point_ids} -> {integer_ids}")
        
        self.client.delete(
            collection_name=collection_name,
            points_selector=integer_ids
        )

    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        if not self.client:
            self.connect()
        
        return self.client.get_collection(collection_name)


qdrant_manager = QdrantManager()
