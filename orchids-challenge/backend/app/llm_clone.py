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
            
            # Enhanced structure with more detailed information
            simplified_context = {
                'url': design_context['url'],
                'base_domain': design_context['base_domain'],
                'title': design_context['structure']['title'],
                'headings': design_context['structure']['headings'],
                'colors': design_context['colors'][:30] if len(design_context['colors']) > 30 else design_context['colors'],
                'fonts': design_context['fonts'],
                'layout': design_context['layout'],
                'meta_tags': design_context['meta_tags'],
                'navigation_links': design_context['navigation_links'],
                'ui_components': design_context.get('ui_components', {}),
                'css_rules': design_context.get('css_rules', [])[:50] if design_context.get('css_rules') and len(design_context['css_rules']) > 50 else design_context.get('css_rules', []),
                'inline_styles': design_context.get('inline_styles', ''),
                'favicon': design_context.get('favicon')
            }
            
            system_prompt = """You are an expert web designer and developer specializing in pixel-perfect website cloning. Your task is to create an EXACT clone of a website based on the detailed design context provided. Your clone should be visually indistinguishable from the original website.

            Follow these precise guidelines:
            1. Create a complete HTML file with <!DOCTYPE html>, <html>, <head>, and <body> tags.
            2. Implement a pixel-perfect layout that EXACTLY matches the original - pay special attention to spacing, alignment, and component positioning.
            3. Use the EXACT colors, fonts, borders, shadows, and visual effects as the original.
            4. Precisely implement all UI components (navigation, buttons, cards, forms, etc.) to match the original website.
            5. Copy the exact text content where available.
            6. Include the favicon if provided.
            7. Include all CSS directly in <style> tags, following the exact styling patterns shown in css_rules.
            8. Pay extreme attention to detail - match paddings, margins, font sizes, and all other visual elements precisely.
            9. If there are interactive elements, make them appear visually identical to the original.
            10. The goal is to make a clone that is absolutely indistinguishable from the original website.
            
            Your output must be production-ready, valid HTML that can be viewed directly in a browser and looks EXACTLY like the original website. Start directly with the HTML code without any introduction or explanation."""
            
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
                payload["messages"][1]["content"][0]["text"] += "\n\nI've also included a screenshot of the website. This is the most important reference. You MUST use this screenshot as your primary guide to ensure your clone looks exactly like the original website. Analyze every visual detail in this image and replicate it precisely, including all layout elements, spacing, colors, fonts, and component design."
            
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
            
            # Enhanced structure with more detailed information
            simplified_context = {
                'url': design_context['url'],
                'base_domain': design_context['base_domain'],
                'title': design_context['structure']['title'],
                'headings': design_context['structure']['headings'],
                'colors': design_context['colors'][:30] if len(design_context['colors']) > 30 else design_context['colors'],
                'fonts': design_context['fonts'],
                'layout': design_context['layout'],
                'meta_tags': design_context['meta_tags'],
                'navigation_links': design_context['navigation_links'],
                'ui_components': design_context.get('ui_components', {}),
                'css_rules': design_context.get('css_rules', [])[:50] if design_context.get('css_rules') and len(design_context['css_rules']) > 50 else design_context.get('css_rules', []),
                'inline_styles': design_context.get('inline_styles', ''),
                'favicon': design_context.get('favicon')
            }
            
            # Prepare the API request
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            
            prompt = """You are an expert web designer and developer specializing in pixel-perfect website cloning. Your task is to create an EXACT clone of a website based on the detailed design context provided. Your clone should be visually indistinguishable from the original website.

            Follow these precise guidelines:
            1. Create a complete HTML file with <!DOCTYPE html>, <html>, <head>, and <body> tags.
            2. Implement a pixel-perfect layout that EXACTLY matches the original - pay special attention to spacing, alignment, and component positioning.
            3. Use the EXACT colors, fonts, borders, shadows, and visual effects as the original.
            4. Precisely implement all UI components (navigation, buttons, cards, forms, etc.) to match the original website.
            5. Copy the exact text content where available.
            6. Include the favicon if provided.
            7. Include all CSS directly in <style> tags, following the exact styling patterns shown in css_rules.
            8. Pay extreme attention to detail - match paddings, margins, font sizes, and all other visual elements precisely.
            9. If there are interactive elements, make them appear visually identical to the original.
            10. The goal is to make a clone that is absolutely indistinguishable from the original website.
            
            Your output must be production-ready, valid HTML that can be viewed directly in a browser and looks EXACTLY like the original website. Start directly with the HTML code without any introduction or explanation.
            
            Here's the detailed design context extracted from the website:
            
            """
            
            prompt += json.dumps(simplified_context, indent=2)
            
            # Add screenshot reference if available
            if screenshot_base64:
                prompt += "\n\nI've also included a screenshot of the website as an image. This is the most important reference. You MUST use this screenshot as your primary guide to ensure your clone looks exactly like the original website. Analyze every visual detail in this image and replicate it precisely, including all layout elements, spacing, colors, fonts, and component design."
            
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
            return self._process_extracted_html(code)
        
        # Check if the code is within a code block without language specification
        if "```" in text and "```" in text[text.find("```") + 3:]:
            start_idx = text.find("```") + 3
            end_idx = text.find("```", start_idx)
            code = text[start_idx:end_idx].strip()
            # Only return if it starts with <!DOCTYPE or <html
            if code.strip().startswith(("<!DOCTYPE", "<html")):
                return self._process_extracted_html(code)
        
        # Check if it's just raw HTML
        if text.strip().startswith(("<!DOCTYPE", "<html")):
            return self._process_extracted_html(text)
            
        # If nothing else works, return the whole text
        return text
        
    def _process_extracted_html(self, html):
        """Process the extracted HTML to ensure it's properly formatted"""
        # Make sure base HTML structure is present
        if "<!DOCTYPE html>" not in html and not html.strip().startswith("<!DOCTYPE"):
            html = "<!DOCTYPE html>\n" + html
            
        if "<html" not in html:
            html = html.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n<html>\n") + "\n</html>"
            
        if "<head>" not in html and "<head " not in html:
            # Insert an empty head if missing
            html = html.replace("<html>", "<html>\n<head>\n</head>")
            html = html.replace("<html lang=\"", "<html lang=\"\n<head>\n</head>")
            
        if "<body>" not in html and "<body " not in html:
            # Insert an empty body if missing
            if "</head>" in html:
                html = html.replace("</head>", "</head>\n<body>")
                html = html + "\n</body>"
            
        # Ensure viewport meta tag is present for responsive design
        if "<meta name=\"viewport\"" not in html and "<meta content=\"width=device-width" not in html:
            viewport_meta = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            if "</head>" in html:
                html = html.replace("</head>", f"{viewport_meta}\n</head>")
            elif "<head>" in html:
                html = html.replace("<head>", f"<head>\n{viewport_meta}")
        
        return html
