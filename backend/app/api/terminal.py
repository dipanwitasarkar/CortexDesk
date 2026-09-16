from fastapi import APIRouter, HTTPException
from app.services.terminal_service import terminal_service
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter()


class CommandAnalysisRequest(BaseModel):
    command: str
    context: Optional[dict] = None


class OutputAnalysisRequest(BaseModel):
    output: str
    command: Optional[str] = None


class CommandSuggestionRequest(BaseModel):
    intent: str
    context: Optional[dict] = None


class HistoryAnalysisRequest(BaseModel):
    history: List[str]
    limit: int = 10


class ErrorExplanationRequest(BaseModel):
    error_message: str
    command: Optional[str] = None


@router.post("/terminal/analyze-command")
async def analyze_command(request: CommandAnalysisRequest):
    """Analyze a terminal command"""
    try:
        result = await terminal_service.analyze_command(
            request.command,
            request.context
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/terminal/analyze-output")
async def analyze_output(request: OutputAnalysisRequest):
    """Analyze terminal output"""
    try:
        result = await terminal_service.analyze_output(
            request.output,
            request.command
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/terminal/explain-error")
async def explain_error(request: ErrorExplanationRequest):
    """Explain a terminal error"""
    try:
        result = await terminal_service.explain_error(
            request.error_message,
            request.command
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Temporarily disabled endpoints due to syntax issues
# @router.post("/terminal/suggest-command")
# async def suggest_command(request: CommandSuggestionRequest):
#     """Suggest a terminal command based on intent"""
#     try:
#         result = await terminal_service.suggest_command(
#             request.intent,
#             request.context
#         )
#         
#         if not result["success"]:
#             raise HTTPException(status_code=500, detail=result["error"])
#         
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/terminal/analyze-history")
# async def analyze_history(request: HistoryAnalysisRequest):
#     """Analyze terminal command history"""
#     try:
#         result = await terminal_service.analyze_history(
#             request.history,
#             request.limit
#         )
#         
#         if not result["success"]:
#             raise HTTPException(status_code=500, detail=result["error"])
#         
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
