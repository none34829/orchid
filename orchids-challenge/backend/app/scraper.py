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
import re
from typing import Dict, Any, List, Optional

import aiofiles
import aiohttp
from dotenv import load_dotenv

# Load environment variables for Browserbase
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Import Browserbase Python client if available
try:
    from browserbase import Browserbase
    BROWSERBASE_AVAILABLE = True
    logger.info("Browserbase SDK detected and available for use")
except ImportError:
    logger.warning("Browserbase SDK not installed. Using default Playwright.")
    BROWSERBASE_AVAILABLE = False

# Note: logger is now defined above

class WebsiteScraper:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        # Browserbase API configuration
        self.browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
        self.browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
        
        # Only use Browserbase if the SDK is available and credentials are set
        self.use_browserbase = (BROWSERBASE_AVAILABLE and 
                               self.browserbase_api_key is not None and 
                               self.browserbase_project_id is not None)
        
        if self.use_browserbase:
            logger.info("Browserbase configuration detected. Will use Browserbase for scraping.")
        else:
            logger.info("Using standard Playwright for scraping. Install Browserbase SDK for enhanced capabilities.")

    async def scrape_website(self, url):
        # Extract the base domain from the URL for resolving relative paths
        parsed_url = urlparse(url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Check if the result is already cached
        cache_key = url.replace("/", "_").replace(":", "_")
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            async with aiofiles.open(cache_file, "r") as f:
                cached_data = json.loads(await f.read())
                logger.info(f"Retrieved cached data for URL: {url}")
                return cached_data
        
        logger.info(f"Starting scraping process for URL: {url}")
        
        if self.use_browserbase:
            # Use Browserbase with stealth mode and proxies for enhanced scraping
            logger.info(f"Using Browserbase with stealth mode for URL: {url}")
            
            try:
                # Initialize Browserbase client
                bb = BrowserBase(api_key=self.browserbase_api_key)
                
                # Create a session with stealth mode and proxy settings
                session_options = {
                    "capabilities": {
                        "stealth_mode": True,  # Enable stealth mode to avoid detection
                        "proxy": {"type": "residential"}  # Use residential proxy to avoid blocks
                    }
                }
                
                # Add project_id if available
                if self.browserbase_project_id:
                    session_options["project_id"] = self.browserbase_project_id
                    
                session = await bb.sessions.create(session_options)
                
                # Connect using Playwright
                browser = await session.connect_with_playwright()
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to URL with generous timeout
                logger.info(f"Connected to Browserbase session {session.id}, navigating to {url}")
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
            except Exception as e:
                logger.error(f"Error with Browserbase: {str(e)}. Falling back to standard Playwright.")
                # Fall back to regular Playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        viewport={"width": 1920, "height": 1080},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    )
                    page = await context.new_page()
                    await page.goto(url, wait_until="networkidle", timeout=60000)
        else:
            # Use regular Playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
                page = await context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
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
                
                # Get all CSS style rules from stylesheets
                css_rules = await page.evaluate('''
                    () => {
                        const styleSheets = Array.from(document.styleSheets);
                        let rules = [];
                        
                        styleSheets.forEach(sheet => {
                            try {
                                if (sheet.cssRules) {
                                    const sheetRules = Array.from(sheet.cssRules)
                                        .map(rule => {
                                            return {
                                                selectorText: rule.selectorText || null,
                                                cssText: rule.cssText || null
                                            };
                                        });
                                    rules = rules.concat(sheetRules);
                                }
                            } catch (e) {
                                // Skip cross-origin stylesheets that can't be accessed
                                console.log('Could not access stylesheet rules');
                            }
                        });
                        
                        return rules;
                    }
                ''')
                
                # Extract computed styles for key elements
                computed_styles = await page.evaluate('''
                    () => {
                        function getComputedStylesForElement(element) {
                            const styles = window.getComputedStyle(element);
                            const relevantStyles = {};
                            
                            // Get relevant CSS properties
                            const properties = [
                                'color', 'background-color', 'background-image', 'font-family', 'font-size', 'font-weight',
                                'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
                                'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
                                'border', 'border-radius', 'border-top', 'border-right', 'border-bottom', 'border-left',
                                'width', 'height', 'max-width', 'max-height', 'min-width', 'min-height',
                                'display', 'position', 'top', 'right', 'bottom', 'left', 'z-index',
                                'flex-direction', 'flex-wrap', 'justify-content', 'align-items', 'align-content', 'flex-grow',
                                'grid-template-columns', 'grid-template-rows', 'grid-gap',
                                'text-align', 'line-height', 'letter-spacing', 'text-decoration', 'text-transform',
                                'box-shadow', 'opacity', 'transform', 'transition', 'animation',
                                'overflow', 'visibility'
                            ];
                            
                            for (const prop of properties) {
                                relevantStyles[prop] = styles.getPropertyValue(prop);
                            }
                            
                            return relevantStyles;
                        }
                        
                        function getElementInfo(element, depth = 0, maxDepth = 3) {
                            if (depth > maxDepth || !element) return null;
                            
                            // Skip hidden elements and script/style tags
                            if (element.tagName === 'SCRIPT' || element.tagName === 'STYLE') return null;
                            
                            const styles = getComputedStylesForElement(element);
                            const rect = element.getBoundingClientRect();
                            
                            // Handle SVG elements specially (SVGAnimatedString issue)
                            let className;
                            if (element.className && typeof element.className === 'object' && element.className.baseVal !== undefined) {
                                // SVG element with SVGAnimatedString
                                className = element.className.baseVal;
                            } else if (element.className) {
                                // Regular DOM element
                                className = element.className.toString();
                            } else {
                                className = null;
                            }
                            
                            const info = {
                                tagName: element.tagName.toLowerCase(),
                                id: element.id || null,
                                className: className,
                                text: element.textContent?.substring(0, 100) || null,
                                attributes: {},
                                styles,
                                position: {
                                    x: rect.x,
                                    y: rect.y,
                                    width: rect.width,
                                    height: rect.height
                                },
                                isInteractive: element.tagName === 'BUTTON' || 
                                               element.tagName === 'A' || 
                                               element.tagName === 'INPUT' ||
                                               element.tagName === 'SELECT' ||
                                               element.tagName === 'TEXTAREA' ||
                                               (element.getAttribute('role') === 'button') ||
                                               (element.getAttribute('onclick') !== null)
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
                                element.tagName === 'ASIDE' || 
                                element.tagName === 'SECTION' || 
                                element.tagName === 'ARTICLE' || 
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
                            'body', 'header', 'footer', 'nav', 'main', 'aside', 'section', 'article',
                            '.header', '.footer', '.navigation', '.container', '.wrapper', '.content', '.sidebar',
                            '.hero', '.banner', '#header', '#footer', '#nav', '#content', '#main', '#sidebar',
                            '.btn', 'button', 'a.button', '.menu', '.card', '.alert', '.notification',
                            'form', 'input', 'select', 'textarea', '.form-control', '.input-group',
                            '.modal', '.dialog', '.overlay', '.popup', '.tooltip',
                            'table', 'tr', 'td', 'th', '.table',
                            'img', 'video', 'audio', 'iframe', '.media', '.image',
                            '.row', '.col', '.column', '.grid', '.flex',
                            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'span', 'div'
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
                                if (depth > 5) return null;  // Increased depth to capture more structure
                                
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
                                        // Handle SVG elements' className properly
                                        let classNameValue;
                                        if (child.className && typeof child.className === 'object' && child.className.baseVal !== undefined) {
                                            classNameValue = child.className.baseVal;
                                        } else if (child.className) {
                                            classNameValue = child.className.toString();
                                        } else {
                                            classNameValue = null;
                                        }
                                        
                                        return {
                                            tag: child.tagName.toLowerCase(),
                                            id: child.id || null,
                                            className: classNameValue,
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
            
            # Extract favicon
            favicon = None
            favicon_tags = soup.find_all('link', rel=lambda r: r and ('icon' in r.lower() or 'shortcut icon' in r.lower()))
            if favicon_tags:
                favicon_href = favicon_tags[0].get('href')
                if favicon_href:
                    if not favicon_href.startswith(('http://', 'https://')):  
                        favicon = urljoin(base_domain, favicon_href)
                    else:
                        favicon = favicon_href
            
            # Extract and categorize UI components
            ui_components = {}
            component_selectors = {
                'buttons': ['button', '.btn', '.button', '[role="button"]'],
                'forms': ['form'],
                'inputs': ['input', 'textarea', 'select'],
                'navigation': ['nav', '.nav', '.navigation', '.menu'],
                'cards': ['.card', '.box', '.panel', '.item'],
                'modals': ['.modal', '.dialog', '.popup', '.overlay'],
                'headers': ['header', '.header', '#header'],
                'footers': ['footer', '.footer', '#footer'],
                'sidebars': ['aside', '.sidebar', '#sidebar'],
            }
            
            for component_type, selectors in component_selectors.items():
                components = []
                for selector in selectors:
                    try:
                        for element in soup.select(selector):
                            components.append({
                                'html': str(element),
                                'text': element.get_text(strip=True),
                                'attributes': {attr: element.get(attr) for attr in element.attrs}
                            })
                    except Exception as e:
                        logger.warning(f"Error extracting {component_type} with selector {selector}: {e}")
                
                ui_components[component_type] = components[:5]  # Limit to first 5 of each type
            
            # Extract CSS styles from style tags
            inline_styles = ""
            for style_tag in soup.find_all('style'):
                inline_styles += style_tag.string or ""
            
            # Compile all scraped data with enhanced information
            design_context = {
                'screenshot': screenshot_base64,
                'url': url,  # Ensure URL is always included, was causing errors before
                'base_domain': base_domain,
                'favicon': favicon,
                'title': structure.get('title', ''),
                'structure': structure,
                'meta_tags': meta_tags,
                'images': images[:20],  # Include more images
                'navigation_links': navigation_links[:30],  # Include more navigation links
                'stylesheets': stylesheets,
                'inline_styles': inline_styles,
                'css_rules': css_rules, 
                'colors': colors,
                'fonts': fonts,
                'computed_styles': computed_styles,
                'layout': layout,
                'ui_components': ui_components,
                'html_sample': str(soup)[:100000]  # Increased to 100k characters of HTML for better fidelity
            }
            
            return design_context

    async def get_cached_website_data(self, url):
        """Check if we have cached data for this URL"""
        # Create a filename from URL (simplified approach)
        filename = base64.b64encode(url.encode()).decode().replace('/', '_') + '.json'
        cache_path = os.path.join(self.cache_dir, filename)  # Use self.cache_dir for consistency
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None
    
    def save_to_cache(self, url, data):
        """Save scraped data to cache"""
        filename = base64.b64encode(url.encode()).decode().replace('/', '_') + '.json'
        cache_path = os.path.join(self.cache_dir, filename)  # Use self.cache_dir for consistency
        
        with open(cache_path, 'w') as f:
            json.dump(data, f)
