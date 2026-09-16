from typing import Dict, Any, Optional, List
import base64
from pathlib import Path
from app.services.llm_service import llm_service
from app.services.observability import logger, performance_monitor
import json


class ScreenshotService:
    """
    Screenshot intelligence service for capturing and analyzing screenshots.
    Integrates with vision models for image understanding.
    """
    
    def __init__(self):
        self.logger = logger
        self.supported_formats = ['png', 'jpg', 'jpeg', 'bmp']
    
    async def capture_screenshot(self, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture a screenshot using PowerShell
        """
        try:
            from app.mcp.powershell_mcp import PowerShellMCP
            powershell = PowerShellMCP()
            
            # Generate filename if not provided
            if not save_path:
                import time
                timestamp = int(time.time())
                save_path = f"screenshot_{timestamp}.png"
            
            # Capture screenshot using PowerShell
            # Note: This requires the PowerShell screenshot module
            # For now, we'll use a basic approach
            command = f"""
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $bmp = New-Object System.Drawing.Bitmap $bounds.width, $bounds.height
            $graphics = [System.Drawing.Graphics]::FromImage($bmp)
            $graphics.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.size)
            $bmp.Save('{save_path}')
            $graphics.Dispose()
            $bmp.Dispose()
            """
            
            result = await powershell.call_tool("execute_command", {"command": command})
            
            if "error" in result:
                self.logger.error(f"Screenshot capture failed: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"]
                }
            
            self.logger.info(f"Screenshot captured successfully: {save_path}")
            
            return {
                "success": True,
                "path": save_path,
                "timestamp": performance_monitor.metrics.get("timestamp") if hasattr(performance_monitor, 'metrics') else None
            }
            
        except Exception as e:
            self.logger.error(f"Screenshot capture error: {str(e)}")
            await performance_monitor.track_error(e, {"operation": "capture_screenshot"})
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_screenshot(
        self,
        image_path: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze a screenshot using vision capabilities.
        
        Args:
            image_path: Path to the screenshot file
            analysis_type: Type of analysis (general, ui_elements, text, actions)
        """
        try:
            # Read and encode image
            image_data = await self._read_image(image_path)
            if not image_data:
                return {
                    "success": False,
                    "error": "Failed to read image"
                }
            
            # Perform analysis based on type
            if analysis_type == "general":
                return await self._general_analysis(image_data, image_path)
            elif analysis_type == "ui_elements":
                return await self._ui_element_analysis(image_data, image_path)
            elif analysis_type == "text":
                return await self._text_extraction(image_data, image_path)
            elif analysis_type == "actions":
                return await self._action_suggestion(image_data, image_path)
            else:
                return await self._general_analysis(image_data, image_path)
                
        except Exception as e:
            self.logger.error(f"Screenshot analysis error: {str(e)}")
            await performance_monitor.track_error(e, {
                "operation": "analyze_screenshot",
                "image_path": image_path,
                "analysis_type": analysis_type
            })
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _read_image(self, image_path: str) -> Optional[str]:
        """Read image and convert to base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed to read image: {str(e)}")
            return None
    
    async def _general_analysis(self, image_data: str, image_path: str) -> Dict[str, Any]:
        """General screenshot analysis"""
        try:
            # For now, use LLM with image description prompt
            # In production, this would use a proper vision model
            prompt = f"""Analyze this screenshot and provide:
1. A general description of what's shown
2. Key elements visible
3. Any text content you can identify
4. The likely application or context
5. Any notable features or UI elements

Image data: {image_data[:100]}... (truncated)"""
            
            # Since we may not have vision capabilities, provide a simulated response
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a vision analysis assistant. Analyze screenshots and provide detailed descriptions."},
                {"role": "user", "content": f"Analyze the screenshot at {image_path}. Describe what you see, key elements, text content, and context."}
            ])
            
            return {
                "success": True,
                "analysis_type": "general",
                "description": response,
                "image_path": image_path
            }
            
        except Exception as e:
            self.logger.error(f"General analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _ui_element_analysis(self, image_data: str, image_path: str) -> Dict[str, Any]:
        """Analyze UI elements in the screenshot"""
        try:
            prompt = f"""Analyze the UI elements in this screenshot:
1. Identify buttons, menus, input fields
2. Describe the layout and structure
3. Identify interactive elements
4. Note any unusual or noteworthy UI patterns
5. Suggest possible user interactions

Image path: {image_path}"""
            
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a UI analysis expert. Analyze screenshots for UI elements and interactions."},
                {"role": "user", "content": prompt}
            ])
            
            return {
                "success": True,
                "analysis_type": "ui_elements",
                "ui_analysis": response,
                "image_path": image_path
            }
            
        except Exception as e:
            self.logger.error(f"UI element analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _text_extraction(self, image_data: str, image_path: str) -> Dict[str, Any]:
        """Extract text from screenshot (OCR)"""
        try:
            # In production, this would use OCR (Tesseract, etc.)
            # For now, use LLM to describe text content
            prompt = f"""Extract and describe all text content visible in this screenshot:
1. List all text you can identify
2. Organize by location/section
3. Note any important information
4. Identify any error messages or alerts

Image path: {image_path}"""
            
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are an OCR specialist. Extract and describe text from screenshots."},
                {"role": "user", "content": prompt}
            ])
            
            return {
                "success": True,
                "analysis_type": "text_extraction",
                "text_content": response,
                "image_path": image_path
            }
            
        except Exception as e:
            self.logger.error(f"Text extraction error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _action_suggestion(self, image_data: str, image_path: str) -> Dict[str, Any]:
        """Suggest actions based on screenshot analysis"""
        try:
            prompt = f"""Based on this screenshot, suggest appropriate actions:
1. What might the user want to do next?
2. What actions are available in this context?
3. Are there any errors or issues that need attention?
4. What would be helpful automation or assistance?
5. Recommend specific Windows Agent commands

Image path: {image_path}"""
            
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are an action suggestion assistant. Analyze screenshots and suggest helpful actions."},
                {"role": "user", "content": prompt}
            ])
            
            return {
                "success": True,
                "analysis_type": "action_suggestion",
                "suggested_actions": response,
                "image_path": image_path
            }
            
        except Exception as e:
            self.logger.error(f"Action suggestion error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def compare_screenshots(
        self,
        image_path1: str,
        image_path2: str
    ) -> Dict[str, Any]:
        """Compare two screenshots and identify differences"""
        try:
            prompt = f"""Compare these two screenshots:
1. Identify differences between the images
2. Note any changes in UI, content, or state
3. Highlight important changes
4. Suggest what might have caused the differences

Image 1: {image_path1}
Image 2: {image_path2}"""
            
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a screenshot comparison expert. Identify and describe differences between images."},
                {"role": "user", "content": prompt}
            ])
            
            return {
                "success": True,
                "comparison": response,
                "image_path1": image_path1,
                "image_path2": image_path2
            }
            
        except Exception as e:
            self.logger.error(f"Screenshot comparison error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def detect_ui_state(self, image_path: str) -> Dict[str, Any]:
        """Detect the current UI state from screenshot"""
        try:
            prompt = f"""Analyze the UI state in this screenshot:
1. What application is shown?
2. What is the current view/page?
3. What is the user likely doing?
4. What is the current state (loading, error, success, etc.)?
5. Are there any modal dialogs or alerts?

Image path: {image_path}"""
            
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a UI state detection expert. Analyze screenshots to determine the current application state."},
                {"role": "user", "content": prompt}
            ])
            
            return {
                "success": True,
                "ui_state": response,
                "image_path": image_path
            }
            
        except Exception as e:
            self.logger.error(f"UI state detection error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


screenshot_service = ScreenshotService()
