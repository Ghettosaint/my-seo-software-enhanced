"""
Readability scoring utilities.

This module wraps the ``textstat`` library to compute a basic
readability score for a piece of text.  If ``textstat`` is not
available the module falls back to a simple implementation of the
Flesch reading ease formula.  The ``compute_readability`` function
returns a dictionary with the calculated score and a qualitative
interpretation.
"""

import re
from typing import Dict

try:
    from textstat import flesch_reading_ease  # type: ignore
    _USE_TEXTSTAT = True
except ImportError:
    _USE_TEXTSTAT = False


def _syllable_count(word: str) -> int:
    """Approximate syllable count for a single word.

    This helper is a crude heuristic used when ``textstat`` is not
    available.  It counts vowel groups in a word and makes a few
    adjustments for silent vowels and special endings.  It is not
    perfect but provides a reasonable estimate for readability
    calculations.
    """
    word = word.lower()
    word = re.sub(r'[^a-z]', '', word)
    vowels = 'aeiouy'
    num_vowels = 0
    prev_char_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_char_was_vowel:
            num_vowels += 1
        prev_char_was_vowel = is_vowel

    # Subtract silent 'e'
    if word.endswith('e') and num_vowels > 1:
        num_vowels -= 1
    return max(1, num_vowels)


def _flesch_reading_ease_manual(text: str) -> float:
    words = re.findall(r'[A-Za-z]+', text)
    sentences = re.split(r'[.!?]', text)
    words_count = len(words) if words else 1
    sentences_count = len([s for s in sentences if s.strip()]) or 1
    syllables_count = sum(_syllable_count(word) for word in words)

    words_per_sentence = words_count / sentences_count
    syllables_per_word = syllables_count / words_count

    return 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)


def compute_readability(text: str) -> Dict[str, float]:
    """Compute the Flesch reading ease score for the given text.

    Args:
        text: The input passage.

    Returns:
        A dictionary with the numeric score and a human‑readable
        interpretation.  Higher scores indicate easier reading.
    """
    if _USE_TEXTSTAT:
        try:
            score = flesch_reading_ease(text)
        except Exception:
            score = _flesch_reading_ease_manual(text)
    else:
        score = _flesch_reading_ease_manual(text)

    # Interpret the score according to common ranges
    if score >= 90:
        level = 'Very easy (5th grade)'
    elif score >= 80:
        level = 'Easy (6th grade)'
    elif score >= 70:
        level = 'Fairly easy'
    elif score >= 60:
        level = 'Standard (8th–9th grade)'
    elif score >= 50:
        level = 'Fairly difficult (10th–12th grade)'
    elif score >= 30:
        level = 'Difficult (college)'
    else:
        level = 'Very confusing'

    return {
        'score': round(score, 2),
        'level': level
    }
