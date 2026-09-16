from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.document_service import document_service
from app.api.schemas import DocumentCreate, DocumentResponse
from typing import Dict, Any, Optional, List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/documents", response_model=DocumentResponse)
async def create_document(document: DocumentCreate):
    """Create a new document"""
    try:
        document_id = await document_service.create_document(
            user_id=1,  # TODO: Get from auth
            title=document.title,
            file_type=document.file_type,
            content=document.content,
            file_path=document.file_path,
            metadata=document.meta_data
        )
        
        # Process document if content is provided
        if document.content:
            await document_service.process_document(document_id, document.content)
        
        doc_data = await document_service.get_document(document_id)
        return DocumentResponse(**doc_data)
    except Exception as e:
        logger.error(f"Failed to create document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")


@router.post("/documents/text")
async def create_text_document(
    title: str,
    content: str,
    metadata: Optional[str] = None
):
    """Create and process a text document in one step"""
    try:
        import json
        meta_dict = json.loads(metadata) if metadata else None
        
        document_id = await document_service.process_text_content(
            user_id=1,  # TODO: Get from auth
            title=title,
            text_content=content,
            metadata=meta_dict
        )
        
        doc_data = await document_service.get_document(document_id)
        return {
            "document_id": document_id,
            "document": doc_data,
            "message": "Document created and processed successfully"
        }
    except Exception as e:
        logger.error(f"Failed to create text document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create text document: {str(e)}")


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    user_id: int = 1,  # TODO: Get from auth
    limit: int = 50,
    offset: int = 0
):
    """List all documents for a user"""
    try:
        documents = await document_service.list_documents(user_id, limit, offset)
        return [DocumentResponse(**doc) for doc in documents]
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int):
    """Get a specific document"""
    try:
        doc_data = await document_service.get_document(document_id)
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        return DocumentResponse(**doc_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.delete("/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document"""
    try:
        success = await document_service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully", "document_id": document_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.post("/documents/{document_id}/process")
async def process_document(document_id: int):
    """Process a document (chunking + embedding)"""
    try:
        doc_data = await document_service.get_document(document_id)
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not doc_data["content"]:
            raise HTTPException(status_code=400, detail="Document has no content to process")
        
        result = await document_service.process_document(document_id, doc_data["content"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.post("/documents/search")
async def search_documents(
    query: str,
    user_id: int = 1,  # TODO: Get from auth
    limit: int = 5
):
    """Search documents using semantic search"""
    try:
        results = await document_service.search_documents(user_id, query, limit)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Failed to search documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search documents: {str(e)}")