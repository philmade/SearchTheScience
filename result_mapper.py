from loguru import logger
from datetime import datetime
from typing import Dict, Any, Union, List
from schemas import SearchResult, SearchType
from urllib.parse import urlparse


class SearchResultMapper:
    """Handles mapping all search types to unified SearchResult"""

    @classmethod
    def map_ddgs_news(cls, raw: dict) -> SearchResult:
        return SearchResult(
            result_type=SearchType.NEWS,
            title=raw.get("title", "No Title"),
            href=raw.get("link", ""),
            description=raw.get("body"),
            published=raw.get("date"),
            source=raw.get("source", "Unknown"),
            additional_fields={
                "image": raw.get("image"),
                "raw": raw,  # Preserve original structure
            },
        )

    @classmethod
    def map_pubmed(cls, raw: tuple) -> SearchResult:
        pmid, title, background, doi = raw
        return SearchResult(
            result_type=SearchType.SCIENCE_PUBMED,
            title=title.strip(),
            href=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            description=background.strip(),
            source="PubMed",
            doi=doi,
            additional_fields={"pmid": pmid, "background": background, "raw": raw},
        )

    @classmethod
    def map_clinical_trial(cls, raw: dict) -> SearchResult:
        return SearchResult(
            result_type=SearchType.CLINICAL_TRIAL,
            title=raw.get("OfficialTitle", ""),
            href=f"https://clinicaltrials.gov/ct2/show/{raw['NCTId']}",
            description=raw.get("BriefSummary", ""),
            published=raw.get("StartDate", ""),
            source="ClinicalTrials.gov",
            additional_fields={
                "nct_id": raw["NCTId"],
                "phase": raw.get("Phase"),
                "conditions": raw.get("Condition"),
                "raw": raw,
            },
        )

    @classmethod
    def map_ddgs_text(
        cls, raw_result: Dict[str, Any], search_type: SearchType
    ) -> SearchResult:
        return SearchResult(
            result_type=search_type,
            title=raw_result.get("title", ""),
            href=raw_result.get("href", ""),
            description=raw_result.get("body", ""),
            published=None,  # DDGS text results don't have dates
            source=urlparse(raw_result.get("href", "")).netloc or "",
            additional_fields={
                "domain_specific_data": raw_result  # Preserve original structure
            },
        )

    @classmethod
    def map_specialized_search(
        cls, raw_result: Dict[str, Any], search_type: SearchType
    ) -> SearchResult:
        """Handles searches with custom schemas like PubMed/ArXiv"""
        return SearchResult(
            result_type=search_type,
            title=raw_result.get("title", ""),
            href=raw_result.get("url", ""),
            description=raw_result.get("abstract", ""),
            published=raw_result.get("date", ""),
            authors=raw_result.get("authors", []),
            doi=raw_result.get("doi"),
            source=search_type.value,
            additional_fields=raw_result,
        )

    @classmethod
    def map_zenodo(cls, raw: dict) -> SearchResult:
        metadata = raw.get("metadata", {})
        links = raw.get("links", {})

        # Get href with fallbacks
        href = (
            links.get("doi")
            or links.get("html")
            or f"https://zenodo.org/record/{raw.get('id', '')}"
        )

        # Safely get authors
        creators = metadata.get("creators", [])
        authors = [
            c.get("name", "Unknown Author") for c in creators if isinstance(c, dict)
        ]

        # Safely get file types
        files = raw.get("files", [])
        file_types = [f.get("type", "unknown") for f in files if isinstance(f, dict)]

        return SearchResult(
            result_type=SearchType.OPEN_SCIENCE,
            title=metadata.get("title", "Untitled Dataset"),
            href=href,
            description=metadata.get("description", ""),
            published=metadata.get("publication_date"),
            authors=authors,
            doi=raw.get("doi"),
            source="Zenodo",
            additional_fields={
                "file_types": file_types,
                "keywords": metadata.get("keywords", []),
                "raw": raw,
            },
        )

    @classmethod
    def map_openalex(
        cls, raw: Union[dict, list]
    ) -> Union[SearchResult, List[SearchResult]]:
        # If raw is a list, map each item
        if isinstance(raw, list):
            return [cls.map_openalex_item(item) for item in raw]
        # Otherwise map the single item
        return cls.map_openalex_item(raw)

    @classmethod
    def map_openalex_item(cls, raw: dict) -> SearchResult:
        # Convert abstract_inverted_index to readable text if it exists
        abstract = ""
        if raw.get("abstract_inverted_index"):
            # Create a list of tuples (position, word)
            words = [
                (pos[0], word) for word, pos in raw["abstract_inverted_index"].items()
            ]
            # Sort by position and join words
            abstract = " ".join(word for _, word in sorted(words))

        return SearchResult(
            result_type=SearchType.SCIENCE_GENERAL,
            title=raw.get("title", "Untitled Paper"),
            href=raw.get("primary_location", {}).get("pdf_url")
            or f"https://doi.org/{raw.get('doi')}",
            description=abstract,
            published=raw.get("publication_date"),
            authors=[a["author"]["display_name"] for a in raw.get("authorships", [])],
            doi=raw.get("doi"),
            source="OpenAlex",
            additional_fields={
            "related_works": raw.get("related_works", []),
            "referenced_works": raw.get("referenced_works", []),
            "concepts": raw.get("concepts", []),  # <-- Add this line!
            "primary_topic": raw.get("primary_topic", None),  # If available
        },
        )

    @classmethod
    def map_substack(cls, raw: dict) -> SearchResult:
        return SearchResult(
            result_type=SearchType.INDEPENDENT_NEWS,
            title=raw.get("title", "Untitled Post"),
            href=raw.get("canonical_url"),
            description=raw.get("description") or raw.get("truncated_body_text", ""),
            published=raw.get("post_date"),
            authors=[raw.get("author")],
            source=raw.get("publication", "Substack"),
            additional_fields={
                "publication_info": raw.get("publishedBylines"),
                "raw": raw,
            },
        )

    @classmethod
    def map_arxiv(cls, raw: dict) -> SearchResult:
        return SearchResult(
            result_type=SearchType.SCIENCE_ARXIV,
            title=raw.get("title", "Untitled Preprint").strip(),
            href=raw.get("id", ""),
            description=raw.get("summary", "").strip(),
            published=raw.get("published"),
            authors=raw.get("authors", []),
            doi=raw.get("doi"),
            source="arXiv",
            additional_fields={"categories": raw.get("categories", []), "raw": raw},
        )

    @classmethod
    def map_biorxiv(cls, raw: dict) -> SearchResult:
        return SearchResult(
            result_type=SearchType.SCIENCE_BIORXIV,
            title=raw.get("title", "Untitled Preprint"),
            href=f"https://doi.org/{raw.get('doi')}",
            description=raw.get("abstract", ""),
            published=raw.get("date"),
            authors=raw.get("authors", []),
            doi=raw.get("doi"),
            source="bioRxiv",
            additional_fields={
                "category": raw.get("category"),
                "version": raw.get("version"),
                "raw": raw,
            },
        )
