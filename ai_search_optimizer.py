"""
AI search optimisation heuristics.

Large language models and answer‑generating search engines favour pages
that are easy to parse, well‑structured and trustworthy.  This module
implements a set of simple checks on the HTML content of a page and
produces actionable suggestions to improve its visibility in AI
powered search results.  The checks are based on industry
recommendations such as the use of clear heading hierarchies, bullet
lists, structured data and author information.
"""

from bs4 import BeautifulSoup
from typing import Dict, List


def analyze_ai_search_factors(content: str, html: str) -> Dict[str, List[str]]:
    """Analyse a page for features important to AI search optimisation.

    Args:
        content: The plain‑text content of the page.
        html: The raw HTML of the page.

    Returns:
        A dictionary keyed by category with lists of suggestions.
    """
    soup = BeautifulSoup(html, 'html.parser')
    suggestions: Dict[str, List[str]] = {}

    # 1. Heading structure
    headings = {f'h{i}': soup.find_all(f'h{i}') for i in range(1, 7)}
    heading_count = {tag: len(lst) for tag, lst in headings.items()}
    heading_suggestions: List[str] = []
    if heading_count.get('h1', 0) != 1:
        heading_suggestions.append(
            "Use exactly one <h1> heading per page to clearly define the topic."
        )
    if heading_count.get('h2', 0) < 2:
        heading_suggestions.append(
            "Include multiple <h2> subheadings to structure your content into sections."
        )
    if heading_suggestions:
        suggestions['headings'] = heading_suggestions

    # 2. Bulleted or numbered lists
    lists_found = soup.find_all(['ul', 'ol'])
    if not lists_found:
        suggestions.setdefault('lists', []).append(
            "Add bullet or numbered lists to break down complex information into digestible points."
        )

    # 3. Schema markup / structured data
    has_json_ld = bool(soup.find('script', type='application/ld+json'))
    has_microdata = bool(soup.find(attrs={'itemscope': True}) or soup.find(attrs={'itemtype': True}))
    if not (has_json_ld or has_microdata):
        suggestions.setdefault('schema', []).append(
            "Implement schema.org structured data (e.g. Article or FAQ) to help search engines understand your page."
        )

    # 4. Trust and author signals
    author_meta = soup.find('meta', attrs={'name': 'author'})
    author_link = soup.find('a', attrs={'rel': 'author'})
    if not (author_meta or author_link):
        suggestions.setdefault('trust', []).append(
            "Add author information and, if appropriate, credentials or citations to establish trust and expertise."
        )

    # 5. Quick answer / summary at top
    # We check whether the first paragraph is short and summarises the content.  A simple
    # heuristic is to look for the first <p> tag and count its words; if it exceeds
    # 50 words we recommend adding a concise summary or TL;DR.
    first_p = soup.find('p')
    if first_p:
        first_words = first_p.get_text().split()
        if len(first_words) > 50:
            suggestions.setdefault('summary', []).append(
                "Consider adding a concise summary or TL;DR at the beginning of the article to answer common questions quickly."
            )
    else:
        # If no paragraph found the page likely lacks body text.
        suggestions.setdefault('summary', []).append(
            "Add a short introductory paragraph that summarises the page's topic."
        )

    # 6. Conversational tone hint
    # If average sentence length is high we suggest simplifying language.  Here we
    # approximate sentences using periods and count words per sentence.
    sentences = [s.strip() for s in content.split('.') if s.strip()]
    if sentences:
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_len > 25:
            suggestions.setdefault('tone', []).append(
                "Use shorter sentences and a conversational tone to improve readability and user engagement."
            )

    return suggestions
