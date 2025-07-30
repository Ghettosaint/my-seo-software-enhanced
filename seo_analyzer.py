"""
High‑level SEO analysis routine for the modified app.

This module orchestrates the individual analysis components: content
fetching, keyword extraction, readability scoring, performance
measurement and AI search optimisation suggestions.  The
``analyze_url`` function is asynchronous because it relies on
``aiohttp`` for performance analysis and may spawn event loops in the
Flask API.

The returned report is a dictionary ready for JSON serialisation.  In
case of errors in any component the function continues executing
where possible and notes the error in the corresponding section.
"""

import asyncio
import logging
from typing import Dict, Any

from content_analyzer import fetch_content
from keyword_utils import extract_keywords
from readability_utils import compute_readability
from performance_utils import analyze_performance
from ai_search_optimizer import analyze_ai_search_factors

# Configure a basic logger.  In deployment logging is typically
# configured by the hosting platform but this ensures debug output is
# produced during local testing.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def analyze_url(url: str) -> Dict[str, Any]:
    """Analyse a single URL and return a structured report.

    The report includes:

    - ``keyword_analysis``: the top keywords and their counts.
    - ``readability``: a Flesch reading ease score and interpretation.
    - ``performance``: status code, response time and page size.
    - ``ai_search_optimization``: suggestions to improve visibility in
      AI‑powered search results.

    Args:
        url: The URL to analyse.

    Returns:
        A dictionary with the analysis results.
    """
    report: Dict[str, Any] = {'url': url}
    try:
        # 1. Fetch content
        content_data = await fetch_content(url)
        if not content_data:
            report['error'] = 'Failed to fetch content from the URL.'
            return report
        content = content_data['content'] or ''
        html = content_data['full_html'] or ''

        # 2. Keyword analysis
        report['keyword_analysis'] = extract_keywords(content)

        # 3. Readability
        report['readability'] = compute_readability(content)

        # 4. Performance
        report['performance'] = await analyze_performance(url)

        # 5. AI search optimisation suggestions
        report['ai_search_optimization'] = analyze_ai_search_factors(content, html)

    except Exception as exc:
        logger.exception("Unexpected error during analysis: %s", exc)
        report['error'] = f'Unexpected error: {exc}'
    return report
