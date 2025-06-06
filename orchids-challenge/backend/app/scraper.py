import requests
from bs4 import BeautifulSoup
import base64
from playwright.async_api import async_playwright
import asyncio
from urllib.parse import urljoin, urlparse
import os
import logging
import json
from io import BytesIO
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        # Create cache directory if it doesn't exist
        os.makedirs("cache", exist_ok=True)

    async def scrape_website(self, url):
        """
        Main function to scrape a website and extract design context
        """
        logger.info(f"Starting scraping process for URL: {url}")
        
        try:
            # Extract base domain for reference
            parsed_url = urlparse(url)
            base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Use Playwright to get a screenshot, HTML content, and styles
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Navigate to the URL with a timeout of 30 seconds
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Take a screenshot of the full page
                screenshot = await page.screenshot(full_page=True, type="jpeg", quality=80)
                screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
                
                # Get HTML content
                html_content = await page.content()
                
                # Extract stylesheets
                stylesheets = await page.evaluate('''
                    () => Array.from(document.styleSheets)
                        .filter(sheet => sheet.href)
                        .map(sheet => sheet.href)
                ''')
                
                # Extract computed styles for key elements
                computed_styles = await page.evaluate('''
                    () => {
                        function getComputedStylesForElement(element) {
                            const styles = window.getComputedStyle(element);
                            const relevantStyles = {};
                            
                            // Get relevant CSS properties
                            const properties = [
                                'color', 'background-color', 'font-family', 'font-size', 
                                'padding', 'margin', 'border', 'width', 'height',
                                'display', 'flex-direction', 'justify-content', 'align-items',
                                'text-align', 'line-height'
                            ];
                            
                            for (const prop of properties) {
                                relevantStyles[prop] = styles.getPropertyValue(prop);
                            }
                            
                            return relevantStyles;
                        }
                        
                        function getElementInfo(element, depth = 0, maxDepth = 2) {
                            if (depth > maxDepth || !element) return null;
                            
                            // Skip hidden elements and script/style tags
                            if (element.tagName === 'SCRIPT' || element.tagName === 'STYLE') return null;
                            
                            const styles = getComputedStylesForElement(element);
                            const rect = element.getBoundingClientRect();
                            
                            const info = {
                                tagName: element.tagName.toLowerCase(),
                                id: element.id || null,
                                className: element.className || null,
                                text: element.textContent?.substring(0, 100) || null,
                                attributes: {},
                                styles,
                                position: {
                                    x: rect.x,
                                    y: rect.y,
                                    width: rect.width,
                                    height: rect.height
                                }
                            };
                            
                            // Get attributes
                            for (const attr of element.attributes) {
                                info.attributes[attr.name] = attr.value;
                            }
                            
                            // Get important child elements (for key structural elements only)
                            if (element.tagName === 'BODY' || 
                                element.tagName === 'HEADER' || 
                                element.tagName === 'FOOTER' || 
                                element.tagName === 'NAV' || 
                                element.tagName === 'MAIN' || 
                                element.id || 
                                (element.className && element.className.includes('container'))) {
                                
                                info.children = [];
                                for (const child of element.children) {
                                    const childInfo = getElementInfo(child, depth + 1, maxDepth);
                                    if (childInfo) {
                                        info.children.push(childInfo);
                                    }
                                }
                            }
                            
                            return info;
                        }
                        
                        // Start with body and selected key elements
                        const keySelectors = [
                            'body', 'header', 'footer', 'nav', 'main', 
                            '.header', '.footer', '.navigation', '.container',
                            '.hero', '.banner', '#header', '#footer', '#nav',
                            '.btn', 'button', 'a.button', '.menu', '.card'
                        ];
                        
                        const result = {};
                        
                        for (const selector of keySelectors) {
                            try {
                                const elements = document.querySelectorAll(selector);
                                if (elements.length > 0) {
                                    result[selector] = Array.from(elements).map(el => getElementInfo(el));
                                }
                            } catch(e) {
                                console.error(`Error getting info for ${selector}:`, e);
                            }
                        }
                        
                        return result;
                    }
                ''')
                
                # Extract colors
                colors = await page.evaluate('''
                    () => {
                        const colors = new Set();
                        const elements = document.querySelectorAll('*');
                        
                        elements.forEach(el => {
                            const styles = window.getComputedStyle(el);
                            const color = styles.getPropertyValue('color');
                            const bgColor = styles.getPropertyValue('background-color');
                            const borderColor = styles.getPropertyValue('border-color');
                            
                            if (color && color !== 'rgba(0, 0, 0, 0)') colors.add(color);
                            if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)') colors.add(bgColor);
                            if (borderColor && borderColor !== 'rgba(0, 0, 0, 0)') colors.add(borderColor);
                        });
                        
                        return Array.from(colors);
                    }
                ''')
                
                # Extract font information
                fonts = await page.evaluate('''
                    () => {
                        const fonts = new Set();
                        const elements = document.querySelectorAll('*');
                        
                        elements.forEach(el => {
                            const fontFamily = window.getComputedStyle(el).getPropertyValue('font-family');
                            if (fontFamily) fonts.add(fontFamily);
                        });
                        
                        return Array.from(fonts);
                    }
                ''')
                
                # Extract layout structure
                layout = await page.evaluate('''
                    () => {
                        function getLayoutStructure() {
                            const body = document.body;
                            
                            function getStructure(element, depth = 0) {
                                if (depth > 3) return null;  // Limiting depth to avoid huge output
                                
                                const children = Array.from(element.children)
                                    .filter(el => {
                                        // Filter out invisible elements
                                        const rect = el.getBoundingClientRect();
                                        const style = window.getComputedStyle(el);
                                        return rect.width > 0 && 
                                               rect.height > 0 && 
                                               style.display !== 'none' && 
                                               style.visibility !== 'hidden';
                                    })
                                    .map(child => {
                                        const rect = child.getBoundingClientRect();
                                        return {
                                            tag: child.tagName.toLowerCase(),
                                            id: child.id || null,
                                            className: child.className.toString() || null,
                                            position: {
                                                x: rect.x,
                                                y: rect.y,
                                                width: rect.width,
                                                height: rect.height
                                            },
                                            children: getStructure(child, depth + 1)
                                        };
                                    });
                                
                                return children;
                            }
                            
                            return {
                                width: window.innerWidth,
                                height: window.innerHeight,
                                structure: getStructure(body)
                            };
                        }
                        
                        return getLayoutStructure();
                    }
                ''')
                
                # Close browser
                await browser.close()
            
            # Process and resize screenshot to save memory
            img_data = BytesIO(base64.b64decode(screenshot_base64))
            img = Image.open(img_data)
            # Resize to maintain aspect ratio but limit height
            width, height = img.size
            max_height = 1200
            if height > max_height:
                ratio = max_height / height
                new_width = int(width * ratio)
                img = img.resize((new_width, max_height), Image.LANCZOS)
                
                # Save as a new byte array
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                screenshot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Parse HTML with BeautifulSoup for easier extraction
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract meta tags
            meta_tags = []
            for meta in soup.find_all('meta'):
                if meta.get('name') or meta.get('property'):
                    meta_tags.append({
                        'name': meta.get('name', meta.get('property')),
                        'content': meta.get('content')
                    })
            
            # Extract images
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                if not src.startswith(('http://', 'https://')):
                    src = urljoin(base_domain, src)
                
                alt = img.get('alt', '')
                width = img.get('width', '')
                height = img.get('height', '')
                
                images.append({
                    'src': src,
                    'alt': alt,
                    'width': width,
                    'height': height
                })
            
            # Extract links for navigation structure
            navigation_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(base_domain, href)
                
                navigation_links.append({
                    'href': href,
                    'text': a.get_text(strip=True)
                })
            
            # Extract page structure
            structure = {
                'title': soup.title.string if soup.title else '',
                'headings': {
                    'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
                    'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
                    'h3': [h.get_text(strip=True) for h in soup.find_all('h3')],
                }
            }
            
            # Compile all scraped data
            design_context = {
                'screenshot': screenshot_base64,
                'url': url,
                'base_domain': base_domain,
                'structure': structure,
                'meta_tags': meta_tags,
                'images': images[:10],  # Limit to first 10 images
                'navigation_links': navigation_links[:20],  # Limit to first 20 links
                'stylesheets': stylesheets,
                'colors': colors,
                'fonts': fonts,
                'computed_styles': computed_styles,
                'layout': layout,
                'html_sample': str(soup)[:50000]  # First 50k characters of HTML
            }
            
            return design_context
            
        except Exception as e:
            logger.error(f"Error scraping website: {str(e)}")
            raise Exception(f"Failed to scrape website: {str(e)}")
            
    def get_cached_website_data(self, url):
        """Check if we have cached data for this URL"""
        # Create a filename from URL (simplified approach)
        filename = base64.b64encode(url.encode()).decode().replace('/', '_') + '.json'
        cache_path = os.path.join('cache', filename)
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None
            
    def save_to_cache(self, url, data):
        """Save scraped data to cache"""
        filename = base64.b64encode(url.encode()).decode().replace('/', '_') + '.json'
        cache_path = os.path.join('cache', filename)
        
        with open(cache_path, 'w') as f:
            json.dump(data, f)
