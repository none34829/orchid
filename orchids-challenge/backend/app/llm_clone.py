import os
import json
import logging
from typing import Dict, Any
import httpx
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteCloner:
    def __init__(self):
        # Check for environment variables for API keys
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.default_model = "claude" # can be "claude" or "gemini"
        
    async def generate_clone(self, design_context: Dict[Any, Any], model: str = None):
        """
        Generate an HTML clone based on the provided design context
        """
        model = model or self.default_model
        
        if model == "claude":
            if not self.anthropic_api_key:
                raise ValueError("Missing Anthropic API key. Set ANTHROPIC_API_KEY environment variable.")
            return await self._generate_with_claude(design_context)
        elif model == "gemini":
            if not self.google_api_key:
                raise ValueError("Missing Google API key. Set GOOGLE_API_KEY environment variable.")
            return await self._generate_with_gemini(design_context)
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    async def _generate_with_claude(self, design_context):
        """Use Claude API to generate HTML clone"""
        try:
            # Prepare design context for the prompt
            screenshot_base64 = design_context.pop('screenshot', None)
            html_sample = design_context.pop('html_sample', None)
            
            # Simplified structure to reduce token usage
            simplified_context = {
                'url': design_context['url'],
                'title': design_context['structure']['title'],
                'headings': design_context['structure']['headings'],
                'colors': design_context['colors'][:20] if len(design_context['colors']) > 20 else design_context['colors'],
                'fonts': design_context['fonts'],
                'layout': design_context['layout'],
                'meta_tags': design_context['meta_tags'],
                'navigation_links': design_context['navigation_links']
            }
            
            system_prompt = """You are an expert web designer and developer. Your task is to clone a website based on the design context provided. 
            Create a modern, responsive HTML website that matches the visual style and layout of the original as closely as possible.

            Follow these guidelines:
            1. Create a complete HTML file with <!DOCTYPE html>, <html>, <head>, and <body> tags.
            2. Include a responsive design using modern CSS (flexbox/grid).
            3. Match colors, fonts, layout, and overall visual style.
            4. Ensure proper spacing, alignment, and hierarchy.
            5. Implement key UI components like navigation bars, footers, etc.
            6. Use placeholder text for content (can be based on the original).
            7. Keep the design clean and professional.
            8. Only use HTML, CSS, and minimal vanilla JavaScript.
            9. Include all CSS directly in <style> tags.
            10. Avoid using external libraries or frameworks.

            Your output should be production-ready, valid HTML that I can directly view in a browser."""
            
            # Prepare the API request
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Please clone the following website and create HTML code that closely resembles its design. Here's the design context extracted from the website:\n\n{json.dumps(simplified_context, indent=2)}"
                            }
                        ]
                    }
                ]
            }
            
            # Add screenshot if available
            if screenshot_base64:
                payload["messages"][1]["content"].append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": screenshot_base64
                    }
                })
                
                # Add instructions for the image
                payload["messages"][1]["content"][0]["text"] += "\n\nI've also included a screenshot of the website. Please use this as your primary reference for recreating the website's visual appearance."
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response_data = response.json()
                
                if response.status_code != 200:
                    logger.error(f"Error from Claude API: {response_data}")
                    raise Exception(f"Failed to generate HTML clone: {response_data.get('error', {}).get('message', 'Unknown error')}")
                
                generated_html = response_data["content"][0]["text"]
                
                # Extract just the HTML code from the response
                html_code = self._extract_html_code(generated_html)
                
                return {
                    "generated_html": html_code,
                    "model_used": "claude-3-sonnet",
                }
        except Exception as e:
            logger.error(f"Error generating with Claude: {str(e)}")
            raise Exception(f"Failed to generate HTML clone with Claude: {str(e)}")
    
    async def _generate_with_gemini(self, design_context):
        """Use Gemini API to generate HTML clone"""
        try:
            # Prepare design context for the prompt
            screenshot_base64 = design_context.pop('screenshot', None)
            html_sample = design_context.pop('html_sample', None)
            
            # Simplified structure to reduce token usage
            simplified_context = {
                'url': design_context['url'],
                'title': design_context['structure']['title'],
                'headings': design_context['structure']['headings'],
                'colors': design_context['colors'][:20] if len(design_context['colors']) > 20 else design_context['colors'],
                'fonts': design_context['fonts'],
                'layout': design_context['layout'],
                'meta_tags': design_context['meta_tags'],
                'navigation_links': design_context['navigation_links']
            }
            
            # Prepare the API request
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            
            prompt = """You are an expert web designer and developer. Your task is to clone a website based on the design context provided. 
            Create a modern, responsive HTML website that matches the visual style and layout of the original as closely as possible.
            
            Follow these guidelines:
            1. Create a complete HTML file with <!DOCTYPE html>, <html>, <head>, and <body> tags.
            2. Include a responsive design using modern CSS (flexbox/grid).
            3. Match colors, fonts, layout, and overall visual style.
            4. Ensure proper spacing, alignment, and hierarchy.
            5. Implement key UI components like navigation bars, footers, etc.
            6. Use placeholder text for content (can be based on the original).
            7. Keep the design clean and professional.
            8. Only use HTML, CSS, and minimal vanilla JavaScript.
            9. Include all CSS directly in <style> tags.
            10. Avoid using external libraries or frameworks.
            
            Your output should be production-ready, valid HTML that I can directly view in a browser.
            
            Here's the design context extracted from the website:
            
            """
            
            prompt += json.dumps(simplified_context, indent=2)
            
            # Add screenshot reference if available
            if screenshot_base64:
                prompt += "\n\nI've also included a screenshot of the website as an image. Please use this as your primary reference for recreating the website's visual appearance."
            
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 8192,
                    "topP": 0.95,
                    "topK": 64
                }
            }
            
            # Add screenshot if available
            if screenshot_base64:
                payload["contents"][0]["parts"].append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": screenshot_base64
                    }
                })
            
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.google_api_key
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{url}?key={self.google_api_key}", json=payload, headers=headers)
                response_data = response.json()
                
                if "error" in response_data:
                    logger.error(f"Error from Gemini API: {response_data}")
                    raise Exception(f"Failed to generate HTML clone: {response_data.get('error', {}).get('message', 'Unknown error')}")
                
                generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Extract just the HTML code from the response
                html_code = self._extract_html_code(generated_text)
                
                return {
                    "generated_html": html_code,
                    "model_used": "gemini-2.0-flash",
                }
        except Exception as e:
            logger.error(f"Error generating with Gemini: {str(e)}")
            raise Exception(f"Failed to generate HTML clone with Gemini: {str(e)}")
    
    def _extract_html_code(self, text):
        """Extract HTML code from the text response"""
        # Check if the code is within a code block
        if "```html" in text and "```" in text[text.find("```html") + 7:]:
            start_idx = text.find("```html") + 7
            end_idx = text.find("```", start_idx)
            code = text[start_idx:end_idx].strip()
            return code
        
        # Check if the code is within a code block without language specification
        if "```" in text and "```" in text[text.find("```") + 3:]:
            start_idx = text.find("```") + 3
            end_idx = text.find("```", start_idx)
            code = text[start_idx:end_idx].strip()
            # Only return if it starts with <!DOCTYPE or <html
            if code.strip().startswith(("<!DOCTYPE", "<html")):
                return code
        
        # Check if it's just raw HTML
        if text.strip().startswith(("<!DOCTYPE", "<html")):
            return text
            
        # If nothing else works, return the whole text
        return text
