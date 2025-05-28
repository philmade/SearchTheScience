from loguru import logger
from datetime import datetime
from typing import Dict, Any, Union, List
from .schemas import SearchResult, SearchType
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
        try:
            # Convert abstract_inverted_index to readable text if it exists
            abstract = ""
            if raw.get("abstract_inverted_index"):
                try:
                    # Reconstruct abstract from inverted index
                    # Format: {"word": [position1, position2, ...], ...}
                    inverted_index = raw["abstract_inverted_index"]
                    
                    # Find the maximum position to determine abstract length
                    max_pos = 0
                    for positions in inverted_index.values():
                        if positions:
                            max_pos = max(max_pos, max(positions))
                    
                    # Create array to hold words at correct positions
                    words_array = [""] * (max_pos + 1)
                    
                    # Place each word at all its positions
                    for word, positions in inverted_index.items():
                        for pos in positions:
                            if 0 <= pos <= max_pos:
                                words_array[pos] = word
                    
                    # Join words to form abstract
                    abstract = " ".join(words_array).strip()
                    
                except (TypeError, IndexError, AttributeError, ValueError):
                    abstract = ""

            # Safely extract authors
            authors = []
            try:
                authorships = raw.get("authorships", [])
                if authorships:
                    for a in authorships[:10]:  # Limit to first 10 authors
                        if isinstance(a, dict) and "author" in a and isinstance(a["author"], dict):
                            name = a["author"].get("display_name", "")
                            if name:
                                authors.append(name)
            except (TypeError, AttributeError):
                authors = []

            # Safely extract primary location
            primary_location = raw.get("primary_location") or {}
            pdf_url = ""
            venue = ""
            if isinstance(primary_location, dict):
                pdf_url = primary_location.get("pdf_url", "")
                source_info = primary_location.get("source") or {}
                if isinstance(source_info, dict):
                    venue = source_info.get("display_name", "")

            # Create href - prefer PDF, fallback to DOI
            doi = raw.get("doi", "")
            if pdf_url:
                href = pdf_url
            elif doi:
                href = f"https://doi.org/{doi.replace('https://doi.org/', '')}"
            else:
                href = raw.get("id", "")

            # Safely extract concepts
            concepts = []
            try:
                concept_list = raw.get("concepts", [])
                if concept_list:
                    concepts = [
                        c.get("display_name", "") for c in concept_list[:5] 
                        if isinstance(c, dict) and c.get("display_name")
                    ]
            except (TypeError, AttributeError):
                concepts = []

            # Safely extract topic
            primary_topic = ""
            try:
                topic_info = raw.get("primary_topic")
                if isinstance(topic_info, dict):
                    primary_topic = topic_info.get("display_name", "")
            except (TypeError, AttributeError):
                primary_topic = ""

            # Safely extract open access info
            open_access = False
            try:
                oa_info = raw.get("open_access")
                if isinstance(oa_info, dict):
                    open_access = oa_info.get("is_oa", False)
            except (TypeError, AttributeError):
                open_access = False

            return SearchResult(
                result_type=SearchType.SCIENCE_GENERAL,
                title=raw.get("title", "Untitled Paper"),
                href=href,
                description=abstract,
                published=raw.get("publication_date"),
                authors=authors,
                doi=doi,
                source="OpenAlex",
                additional_fields={
                    # Essential metadata only - optimized for LLM token usage
                    "citation_count": raw.get("cited_by_count", 0),
                    "publication_year": raw.get("publication_year"),
                    "open_access": open_access,
                    "concepts": concepts,
                    "primary_topic": primary_topic,
                    "venue": venue,
                    # No related_works to save tokens
                },
            )
        except Exception as e:
            # Fallback for any unexpected data structure
            return SearchResult(
                result_type=SearchType.SCIENCE_GENERAL,
                title=raw.get("title", "Untitled Paper"),
                href=raw.get("id", ""),
                description="",
                published=raw.get("publication_date"),
                authors=[],
                doi=raw.get("doi", ""),
                source="OpenAlex",
                additional_fields={"error": f"Mapping error: {str(e)}"},
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
