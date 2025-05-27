"""
SearchTheScience - A Python package for searching across scientific databases and sources.

This package provides a unified interface for searching across multiple scientific databases
including PubMed, arXiv, OpenAlex, Zenodo, and various academic sources.
"""

from .search_functions import multi_search_interface
from .schemas import SearchType, SearchQuery, SearchResult
from .metasearch import Metasearch

__version__ = "0.1.0"
__all__ = [
    "multi_search_interface",
    "SearchType", 
    "SearchQuery",
    "SearchResult",
    "Metasearch"
]