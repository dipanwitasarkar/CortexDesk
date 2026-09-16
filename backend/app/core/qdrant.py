from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.core.config import settings
from typing import List, Dict, Any, Optional
import uuid


class QdrantManager:
    def __init__(self):
        self.client: Optional[QdrantClient] = None

    def connect(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None
        )

    async def create_collection(self, collection_name: str, vector_size: int = 1536):
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
        
        qdrant_points = []
        for point in points:
            qdrant_points.append(
                PointStruct(
                    id=point.get("id", str(uuid.uuid4())),
                    vector=point["vector"],
                    payload=point.get("payload", {})
                )
            )
        
        self.client.upsert(
            collection_name=collection_name,
            points=qdrant_points
        )

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
        
        self.client.delete(
            collection_name=collection_name,
            points_selector=point_ids
        )

    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        if not self.client:
            self.connect()
        
        return self.client.get_collection(collection_name)


qdrant_manager = QdrantManager()
