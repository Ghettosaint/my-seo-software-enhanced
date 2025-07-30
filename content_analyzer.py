"""
Utilities for fetching and parsing HTML content from the web.

This module is a lightly adapted version of the ``content_analyzer``
component from the user's original project.  It exposes an
asynchronous ``fetch_content`` function that downloads a page using
``requests`` (via a thread pool) and extracts useful pieces of
information using BeautifulSoup.  The result includes a cleaned
``content`` string (with most HTML tags removed), the raw HTML,
meta tags, headings, lists of links, images, scripts and styles.

The function caches results for one hour using a simple TTL cache to
avoid re‑fetching the same URL multiple times during a single run.

Note: This code depends on ``beautifulsoup4``, ``requests`` and
``cachetools``.  These dependencies are declared in ``requirements.txt``.
"""

import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from cachetools import TTLCache
import requests
from typing import Dict, Any, Optional

# Set up a simple TTL cache for fetched pages.  Each entry lives for
# one hour (3600 seconds) and up to 100 pages are cached.
content_cache = TTLCache(maxsize=100, ttl=3600)

async def fetch_content(url: str) -> Optional[Dict[str, Any]]:
    """Download a web page and extract useful information.

    Args:
        url: The URL to fetch.

    Returns:
        A dictionary with keys ``content`` (cleaned text), ``full_html``
        (raw HTML), ``meta_tags`` (title and description), ``headings``
        (h1–h6 values), ``links`` (anchor elements), ``images``
        (image sources and alt text), ``scripts`` and ``styles``.  If
        fetching fails, ``None`` is returned.
    """
    if url in content_cache:
        return content_cache[url]

    try:
        # Use a generic user agent so that servers don’t block the request.
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; SEOAnalyzer/1.0; +https://example.com)'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        main_content = extract_main_content(html_content)

        meta_tags = {
            'title': soup.title.string if soup.title else None,
            'description': soup.find('meta', attrs={'name': 'description'})['content']
                if soup.find('meta', attrs={'name': 'description'}) else None
        }

        headings = {f'h{i}': [h.get_text(strip=True) for h in soup.find_all(f'h{i}')]
                    for i in range(1, 7)}

        links = [
            {'text': a.get_text(strip=True), 'href': a['href']}
            for a in soup.find_all('a', href=True)
        ]

        images = [
            {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'loading': img.get('loading')
            }
            for img in soup.find_all('img')
        ]

        scripts = [
            {
                'src': script.get('src', ''),
                'async': 'async' in script.attrs,
                'defer': 'defer' in script.attrs
            }
            for script in soup.find_all('script', src=True)
        ]

        styles = [
            {'href': link.get('href', '')}
            for link in soup.find_all('link', rel="stylesheet")
        ]

        result = {
            'content': main_content,
            'full_content': soup.get_text(),
            'meta_tags': meta_tags,
            'headings': headings,
            'links': links,
            'images': images,
            'scripts': scripts,
            'styles': styles,
            'full_html': str(soup)
        }

        content_cache[url] = result
        return result
    except requests.RequestException as exc:
        logging.error("Error fetching content from %s: %s", url, exc)
        return None
    except Exception as exc:
        logging.error("Unexpected error fetching content from %s: %s", url, exc)
        return None


def extract_main_content(html_content: str) -> str:
    """Extract the main article/body text from a block of HTML.

    This helper removes common boilerplate elements (navigation,
    headers, footers and sidebars) then returns the text of the
    remaining content.  If no obvious article element is present the
    entire page text is returned.

    Args:
        html_content: Raw HTML markup.

    Returns:
        A plain‑text representation of the main content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove non‑article elements
    for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        tag.decompose()

    # Try to identify an article or main element
    main = soup.find(['article', 'main']) or soup.find('div', class_='content')
    if main:
        return main.get_text(separator=' ', strip=True)
    return soup.get_text(separator=' ', strip=True)
