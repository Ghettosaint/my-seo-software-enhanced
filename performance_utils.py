"""
Performance analysis utilities.

This module provides a simple asynchronous function to measure a
webpage's performance.  Given a URL it will determine the response
status code, the time taken to fetch the page and the size of the
response body in kilobytes.  These metrics provide a rough idea of
how quickly the site loads and how heavy the page is.  More
sophisticated analyses (e.g. checking for HTTP/2, CDN usage or
caching headers) could be added in the future.
"""

import asyncio
import time
import ssl
from typing import Dict
import aiohttp


async def analyze_performance(url: str) -> Dict[str, float]:
    """Measure basic performance characteristics of a page.

    Args:
        url: The URL to test.

    Returns:
        A dictionary containing the HTTP status code, the response
        time in seconds and the approximate size of the response in
        kilobytes.  If fetching fails the dictionary indicates an
        error.
    """
    result: Dict[str, float] = {}
    timeout = aiohttp.ClientTimeout(total=30)
    ssl_context = None
    if url.startswith('https'):
        ssl_context = ssl.create_default_context()

    start_time = time.perf_counter()
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, ssl=ssl_context) as response:
                status = response.status
                content = await response.read()
                end_time = time.perf_counter()
                response_time = end_time - start_time
                page_size_kb = len(content) / 1024
                result = {
                    'status_code': status,
                    'response_time_seconds': round(response_time, 3),
                    'page_size_kb': round(page_size_kb, 2)
                }
    except Exception as exc:
        # On failure return an error indicator
        result = {
            'status_code': -1,
            'error': str(exc)
        }
    return result
