from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.screenshot_service import screenshot_service
from typing import Optional
import os

router = APIRouter()


@router.post("/screenshot/capture")
async def capture_screenshot(save_path: Optional[str] = None):
    """Capture a screenshot"""
    try:
        result = await screenshot_service.capture_screenshot(save_path)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/screenshot/analyze")
async def analyze_screenshot(
    image_path: str,
    analysis_type: str = "general"
):
    """Analyze a screenshot"""
    try:
        result = await screenshot_service.analyze_screenshot(image_path, analysis_type)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/screenshot/upload-analyze")
async def upload_and_analyze_screenshot(
    file: UploadFile = File(...),
    analysis_type: str = "general"
):
    """Upload and analyze a screenshot"""
    try:
        # Save uploaded file
        upload_dir = "uploads/screenshots"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Analyze the screenshot
        result = await screenshot_service.analyze_screenshot(file_path, analysis_type)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/screenshot/compare")
async def compare_screenshots(image_path1: str, image_path2: str):
    """Compare two screenshots"""
    try:
        result = await screenshot_service.compare_screenshots(image_path1, image_path2)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/screenshot/ui-state/{image_path:path}")
async def detect_ui_state(image_path: str):
    """Detect UI state from screenshot"""
    try:
        result = await screenshot_service.detect_ui_state(image_path)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
