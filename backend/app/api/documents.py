from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.document_service import document_service
from app.api.schemas import DocumentCreate, DocumentResponse
from typing import Dict, Any, Optional, List
import logging
import os
import tempfile

router = APIRouter()
logger = logging.getLogger(__name__)

# Supported file types
SUPPORTED_TEXT_EXTENSIONS = {'.txt', '.md', '.json', '.csv', '.xml', '.html', '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.css', '.sql'}
SUPPORTED_DOCUMENT_EXTENSIONS = {'.pdf', '.docx', '.doc', '.pptx', '.ppt', '.odt', '.rtf'}
SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}

def get_file_type(filename: str) -> str:
    """Determine file type from extension"""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in SUPPORTED_TEXT_EXTENSIONS:
        return 'text'
    elif ext in SUPPORTED_DOCUMENT_EXTENSIONS:
        return 'document'
    elif ext in SUPPORTED_IMAGE_EXTENSIONS:
        return 'image'
    else:
        return 'unknown'


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


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a file and process it"""
    try:
        # Check file type
        file_type = get_file_type(file.filename)
        
        if file_type == 'unknown':
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: text files, PDFs, Word docs, PowerPoint, images"
            )
        
        # Read file content
        content = await file.read()
        
        # Process based on file type
        if file_type == 'text':
            # Text files - decode directly
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text_content = content.decode('latin-1')
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Failed to decode text file: {str(e)}")
            
            # Create and process document
            document_id = await document_service.process_text_content(
                user_id=1,
                title=file.filename,
                text_content=text_content,
                metadata={"source": "upload", "file_type": file_type}
            )
            
        elif file_type == 'document':
            # Document files (PDF, DOCX, PPTX) - save to temp file and extract text
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text based on file type
                text_content = await document_service.extract_text_from_file(temp_file_path, file.filename)
                
                # Create and process document
                document_id = await document_service.process_text_content(
                    user_id=1,
                    title=file.filename,
                    text_content=text_content,
                    metadata={"source": "upload", "file_type": file_type}
                )
            finally:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        elif file_type == 'image':
            # Image files - save to temp file and extract text using OCR
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text using OCR
                text_content = await document_service.extract_text_from_image(temp_file_path)
                
                # Create and process document
                document_id = await document_service.process_text_content(
                    user_id=1,
                    title=file.filename,
                    text_content=text_content,
                    metadata={"source": "upload", "file_type": file_type}
                )
            finally:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        # Get document data
        doc_data = await document_service.get_document(document_id)
        
        return {
            "document_id": document_id,
            "document": doc_data,
            "message": f"File '{file.filename}' uploaded and processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


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