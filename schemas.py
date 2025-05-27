from pydantic import BaseModel, Field
from typing import Optional, List, Union, Dict, Any
from enum import Enum
from datetime import datetime


class SearchType(Enum):
    """Search types with detailed descriptions for AI context"""

    ADVANCED = "Advanced search that restricts the search to a specific domain - pass the query with site:domain.com"

    WEB = (
        "General web search that finds relevant web pages, documents, and resources "
        "across the entire internet. Accepts site:domain.com restrictions - use these to narrow down results."
    )

    NEWS = (
        "Recent news articles from major news organizations and press outlets. "
        "Focuses on current events, breaking news, and recent developments."
    )

    INDEPENDENT_NEWS = (
        "Articles from independent journalists, newsletters, and alternative media sources. "
        "Good for diverse perspectives and in-depth analysis."
    )

    SCIENCE_PUBMED = (
        "Medical and biomedical research papers from PubMed database. "
        "Includes clinical studies, medical journals, and healthcare research."
    )

    SCIENCE_GENERAL = (
        "Scientific papers and citations across all fields. "
        "Covers physics, chemistry, biology, and interdisciplinary research."
    )

    SCIENCE_ARXIV = (
        "Preprints from arXiv covering physics, mathematics, computer science, and related fields. "
        "Latest research before formal peer review."
    )

    SCIENCE_BIORXIV = (
        "Biology preprints from bioRxiv. "
        "Latest biological research before formal peer review."
    )

    ACADEMIC_PROFILES = (
        "Research profiles, citations, and academic credentials. "
        "Find researchers, their work, and institutional affiliations."
    )

    SEMANTIC_SCHOLAR = (
        "Academic papers with AI-powered relevance ranking. "
        "Smart search across multiple disciplines with citation analysis."
    )

    RESEARCHGATE = (
        "Scientific papers and researcher profiles from ResearchGate. "
        "Includes preprints, technical reports, and researcher networking."
    )

    PAPERITY = (
        "Open access academic papers across multiple disciplines. "
        "Free full-text research papers and journals."
    )

    GOOGLE_SCHOLAR = (
        "Academic papers and citations from Google Scholar. "
        "Comprehensive academic search with citation metrics."
    )

    ACADEMIC_SOURCES = (
        "Combined search across multiple academic databases. "
        "Broad coverage of scholarly content and research outputs."
    )

    OPEN_SCIENCE = (
        "Open access repositories and databases. "
        "Freely available research papers and datasets."
    )

    REFERENCE = (
        "Reference materials, documentation, and educational resources. "
        "Background information and learning materials."
    )

    ZENODO = (
        "Research outputs from the Zenodo repository. "
        "Includes datasets, software, presentations, and papers."
    )
    SCHOLAR = (
        "Academic papers and citations from Google Scholar. "
        "Comprehensive academic search with citation metrics."
    )
    PDF = (
        "PDF files from the web. "
        "Includes research papers, technical reports, and other documents."
    )

    def __str__(self) -> str:
        """Return the description for use in prompts and documentation."""
        return self.value


class SearchTypeFocused(Enum):
    """Search types with detailed descriptions for AI context. This focuses in the AI a little more."""

    INDEPENDENT_NEWS = SearchType.INDEPENDENT_NEWS.value

    SCIENCE_PUBMED = SearchType.SCIENCE_PUBMED.value

    SCIENCE_GENERAL = SearchType.SCIENCE_GENERAL.value

    SCIENCE_ARXIV = SearchType.SCIENCE_ARXIV.value

    ZENODO = SearchType.ZENODO.value

    SCHOLAR = SearchType.SCHOLAR.value


class SearchQuery(BaseModel):
    """Search query with search type and query string. Example, search_type: SearchType.SCIENCE_PUBMED, query: 'cancer'"""

    search_type: SearchType = Field(
        ...,
        description="Search type to use",
    )
    query: str = Field(..., description="Search query string")


class OpenAlexSearch(BaseModel):
    """Search query with search type and query string. Example, search_type: SearchType.SCIENCE_PUBMED, query: 'cancer'"""

    queries: List[str] = Field(
        ...,
        description="List of queries to search for, they'll be run in parallel and the results will be merged",
    )


class SearchResult(BaseModel):
    """Universal search result container for all search_functions.py"""

    result_type: SearchType
    title: Optional[str]
    href: str
    description: Optional[str] = None
    published: Optional[Union[datetime, str]] = None
    authors: List[str] = []
    source: str
    doi: Optional[str] = None
    additional_fields: Dict[str, Any] = Field(default_factory=dict)

    def format_title(self) -> str:
        """Format title with consistent spacing and alignment"""
        if not self.title:
            return ""
        # Remove extra whitespace and center title
        title = " ".join(self.title.split())
        return f"# {title}\n"

    def format_url(self) -> str:
        """Format URL with consistent spacing"""
        return f"\nURL: {self.href}\n"

    def format_description(self) -> str:
        """Format body with consistent spacing"""
        if not self.description:
            return "None\n"
        # Remove extra whitespace and normalize paragraphs
        description = " ".join(self.description.split())
        return f"\n{description}\n"

    def format_additional_metadata(self) -> str:
        """Format metadata section with consistent spacing"""
        metadata = []
        metadata.append("\n### Additional Information")
        metadata.extend(self._get_additional_metadata())
        return "\n".join(metadata) + "\n"

    def _format_header(self) -> str:
        """Unified header formatting"""
        title = self.title or "Untitled Result"
        url = self.href or getattr(self, "url", None) or "No URL available"
        return f"## {title}\n\n**URL:** [{url}]({url})"

    def _get_additional_metadata(self) -> List[str]:
        """Override in subclasses to add additional metadata"""
        return []

    def _format_authors(self, max_authors: int = 5) -> str:
        """Format author list with truncation"""
        if not self.authors:
            return "No authors listed"
        if len(self.authors) <= max_authors:
            return ", ".join(self.authors)
        return f"{', '.join(self.authors[:max_authors])} et al."

    def _format_date(self, date: Union[datetime, str]) -> str:
        """Format date consistently"""
        if isinstance(date, datetime):
            return date.strftime("%Y-%m-%d")
        return str(date)

    def _truncate_text(self, text: str, max_length: int = 1000) -> str:
        """Smart truncation that preserves sentence boundaries"""
        if len(text) <= max_length:
            return text

        # Find the last sentence end before max_length
        truncated = text[:max_length]
        last_period = truncated.rfind(". ")
        last_exclamation = truncated.rfind("! ")
        last_question = truncated.rfind("? ")

        end_index = max(last_period, last_exclamation, last_question)

        if end_index > 0:
            return text[: end_index + 1] + ".. (truncated)"
        return text[:max_length] + "..."

    def _format_search_type(self) -> str:
        """Format search type with consistent spacing"""
        return f"**Search Type:** {self.__class__.__name__}"

    def to_markdown(self, index: Optional[int] = None) -> str:
        """Minimal, token-efficient markdown format"""
        sections = []

        # Index and title
        if index is not None:
            sections.append(f"### {index + 1}. {self.title}")
        else:
            sections.append(f"## {self.title}")

        # URL
        sections.append(f"URL: {self.href}")

        # Core metadata in single line
        meta = []
        if self.authors:
            meta.append(f"Authors: {', '.join(self.authors[:3])}")
        if self.published:
            meta.append(f"Published: {self.published}")
        if meta:
            sections.append(" | ".join(meta))

        # Description
        if self.description:
            sections.append(self.description)

        # Essential footer info
        if self.source or self.doi:
            footer = []
            if self.source:
                footer.append(f"Source: {self.source}")
            if self.doi:
                footer.append(f"DOI: {self.doi}")
            sections.append(" | ".join(footer))

        sections.append("---")
        return "\n\n".join(sections)
