"""
Package initializer for the modified SEO application.

This package exposes the high‑level analysis routine via the
``seo_analyzer`` module and registers the Flask application in
``app.py``.  Modules in this package were built from the original
project's codebase but trimmed and simplified to run as a standalone
service.  The focus is on providing a clean interface for analysing a
single URL, computing keyword statistics, basic readability and
performance metrics, and generating AI search optimisation hints.
"""

from .seo_analyzer import analyze_url  # noqa: F401
