"""
Simplified keyword extraction utilities.

The original project used a sophisticated ``KeywordAnalyzer`` class based
on NLTK and TF–IDF.  For the purposes of this lightweight service we
focus on extracting the most frequent words from the page content
after removing common stop words and punctuation.  The
``extract_keywords`` function returns a list of dictionaries sorted by
descending frequency.  Each entry contains the keyword itself and
its count in the document.
"""

import re
from collections import Counter
from typing import List, Dict

# A minimal set of English stop words.  This list was distilled from
# widely available stop word lists; additional terms can be added as
# needed.  We avoid pulling in NLTK to keep dependencies light.
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for',
    'from', 'if', 'in', 'into', 'is', 'it', 'no', 'not', 'of', 'on',
    'or', 'such', 'that', 'the', 'their', 'then', 'there', 'these',
    'they', 'this', 'to', 'was', 'will', 'with', 'we', 'you', 'your'
}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]{1,}")


def extract_keywords(text: str, top_n: int = 15) -> List[Dict[str, int]]:
    """Extract the most common keywords from a block of text.

    Args:
        text: The input text from which to extract keywords.
        top_n: The number of keywords to return (default 15).

    Returns:
        A list of dictionaries with keys ``keyword`` and ``count``.  The
        list is sorted in descending order of frequency.
    """
    # Normalize text: lower‑case and remove non‑word characters.
    words = [match.group(0).lower() for match in WORD_RE.finditer(text)]

    # Filter out stop words and very short tokens.
    filtered = [w for w in words if w not in STOP_WORDS and len(w) > 2]

    counts = Counter(filtered)

    # Return the top N keywords with their counts.
    most_common = counts.most_common(top_n)
    return [{'keyword': kw, 'count': count} for kw, count in most_common]
