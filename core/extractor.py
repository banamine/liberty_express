cat > core/extractor.py << 'EOF'
"""
Link extraction and content parsing logic
"""

from bs4 import BeautifulSoup
import requests
import logging
from urllib.parse import urljoin

from core.models import LinkItem
from utils.exceptions import ExtractionError, NetworkError

logger = logging.getLogger(__name__)

class LinkExtractor:
    """Extracts and processes links from web pages"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def extract_links(self, url, html_content):
        """Extract links from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')  # Using html.parser as fallback
        return self._extract_links_from_soup(soup, url)
        
    def _extract_links_from_soup(self, soup, base_url):
        """Extract links using configurable CSS selector"""
        main_selector = self.config.get("extraction", {}).get(
            "main_ul_selector",
            "ul"
        )
        
        # Try config selector first
        elements = soup.select(main_selector)
        
        if not elements:
            # Fallback: find ul with most links
            uls = soup.find_all('ul')
            if not uls:
                raise ExtractionError("No navigation elements found")
                
            elements = [max(uls, key=lambda ul: len(ul.find_all('a')))]
            logger.warning(f"Config selector '{main_selector}' failed, using heuristic fallback")
            
        # Extract links from found elements
        links = []
        for element in elements:
            for a in element.find_all('a', href=True):
                href = a['href']
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                
                # Only include HTTP/HTTPS URLs
                if absolute_url.startswith(('http://', 'https://')):
                    # Extract title and description
                    title = a.get_text(strip=True) or "Untitled"
                    description = a.get('title', '')
                    
                    links.append(LinkItem(title, absolute_url, description))
                    
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link.url not in seen:
                seen.add(link.url)
                unique_links.append(link)
                
        logger.info(f"Extracted {len(unique_links)} unique links")
        return unique_links
        
    def fetch_url(self, url, timeout=None, max_retries=None):
        """Fetch URL content with retries"""
        timeout = timeout or self.config.get('timeout', 10)
        max_retries = max_retries or self.config.get('retries', 3)
        
        if max_retries <= 0:
            raise NetworkError("retries must be > 0")
            
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching URL (attempt {attempt + 1}/{max_retries}): {url}")
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                response.encoding = response.apparent_encoding or 'utf-8'
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise NetworkError(f"Failed after {max_retries} attempts: {e}")
                    
                wait = 2 ** attempt  # Exponential backoff
                import time
                time.sleep(wait)
                
        return None  # Should never reach here
EOF