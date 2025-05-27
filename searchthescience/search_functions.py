import asyncio
import aiohttp
from duckduckgo_search import DDGS
from functools import partial
from .schemas import (
    SearchResult,
    SearchType,
    SearchTypeStable,
    SearchQuery,
    SearchQueryAlpha,
)
from .enums import PubMedFilterType
from loguru import logger
from typing import Any
import re
from typing import List, Optional, Union
import xml.etree.ElementTree as ET
from pytrials.client import ClinicalTrials
from yarl import URL
from pyalex import Works
from pyalex import config as pyalex_config
from rank_bm25 import BM25Okapi
import tiktoken
from .result_mapper import SearchResultMapper
import os

max_results = 10


class DDGSManager:
    def __init__(self, proxy=None, timeout=30):
        self.proxy = proxy
        self.timeout = timeout

    def get_ddgs(self):
        return DDGS(proxy=self.proxy, timeout=self.timeout)

    async def run_search(self, search_func, query, max_results=10):
        loop = asyncio.get_running_loop()
        with self.get_ddgs() as ddgs:
            return await loop.run_in_executor(
                None, partial(search_func, ddgs, query, max_results)
            )


def _perform_text_search(ddgs: DDGS, query: str, max_results: int):
    try:
        return list(
            ddgs.text(
                keywords=query,
                region="wt-wt",
                safesearch="off",
                max_results=max_results,
            )
        )
    except Exception as e:
        logger.error(f"Text search error: {str(e)}")
        return []


def _perform_news_search(ddgs: DDGS, query: str, max_results: int):
    try:
        return list(
            ddgs.news(
                keywords=query,
                region="wt-wt",
                safesearch="off",
                max_results=max_results,
            )
        )
    except Exception as e:
        logger.error(f"News search error: {str(e)}")
        return []


# Initialize single manager instance with optional proxy
proxy = os.getenv('PROXY_AUTH')
ddgs_manager = DDGSManager(proxy=f"http://{proxy}@geo.iproyal.com:12321" if proxy else None)


async def search_web(query: str, max_results: int = 10) -> List[SearchResult]:
    results = await ddgs_manager.run_search(_perform_text_search, query, max_results)
    return [SearchResultMapper.map_ddgs_text(r, SearchType.WEB) for r in results]


async def search_news(query: str, max_results: int = 10) -> List[SearchResult]:
    results = await ddgs_manager.run_search(_perform_news_search, query, max_results)
    return [SearchResultMapper.map_ddgs_news(r) for r in results]


async def search_semantic(query: str, max_results: int = 10) -> List[SearchResult]:
    query = f"{query} TLDR site:semanticscholar.org"
    results = await ddgs_manager.run_search(_perform_text_search, query, max_results)
    return [
        SearchResultMapper.map_ddgs_text(r, SearchType.SEMANTIC_SCHOLAR)
        for r in results
    ]


async def search_researchgate(query: str, max_results: int = 10) -> List[SearchResult]:
    query = f"{query} site:researchgate.net"
    results = await ddgs_manager.run_search(_perform_text_search, query, max_results)
    return [
        SearchResultMapper.map_ddgs_text(r, SearchType.RESEARCHGATE) for r in results
    ]


async def search_paperity(query: str, max_results: int = 10) -> List[SearchResult]:
    query = f"{query} site:paperity.org"
    results = await ddgs_manager.run_search(_perform_text_search, query, max_results)
    return [SearchResultMapper.map_ddgs_text(r, SearchType.PAPERITY) for r in results]


async def search_scholar(query: str, max_results: int = 10) -> List[SearchResult]:
    query = f"{query} site:scholar.google.com"
    results = await ddgs_manager.run_search(_perform_text_search, query, max_results)
    return [SearchResultMapper.map_ddgs_text(r, SearchType.SCHOLAR) for r in results]


async def search_academic_sources(
    query: str, max_results: int = 10
) -> List[SearchResult]:
    site_searches = [
        "site:scholar.google.com",
        "site:ncbi.nlm.nih.gov/pubmed",
        "site:onlinelibrary.wiley.com",
        "site:ieeexplore.ieee.org",
        "site:dl.acm.org",
        "site:link.springer.com",
        "site:sciencedirect.com",
        "site:biorxiv.org",
    ]
    query = f"{query} conclusion {' OR '.join(site_searches)}"
    results = await ddgs_manager.run_search(_perform_text_search, query, max_results)
    return [
        SearchResultMapper.map_ddgs_text(r, SearchType.ACADEMIC_SOURCES)
        for r in results
    ]


async def search_open_science_sources(
    query: str, max_results: int = 10
) -> List[SearchResult]:
    site_searches = [
        "site:semanticscholar.org",
        "site:paperity.org",
        "site:researchgate.net",
    ]
    query = f"{query} conclusion {' OR '.join(site_searches)}"
    results = await ddgs_manager.run_search(_perform_text_search, query, max_results)
    return [
        SearchResultMapper.map_ddgs_text(r, SearchType.OPEN_SCIENCE) for r in results
    ]


async def search_reference(query: str, max_results: int = 10) -> List[SearchResult]:
    site_restrictions = [
        "site:*.gov",
        "site:*.edu",
        "site:data.worldbank.org",
        "site:data.un.org",
        "site:oecd.org",
        "site:eurostat.ec.europa.eu",
        "site:statista.com",
        "site:census.gov",
        "site:bls.gov",
        "site:who.int/data",
        "site:imf.org/en/Data",
    ]
    query = (
        f"{query} (statistics OR data OR figures) ({' OR '.join(site_restrictions)})"
    )
    results = await ddgs_manager.run_search(_perform_text_search, query, max_results)
    return [SearchResultMapper.map_ddgs_text(r, SearchType.REFERENCE) for r in results]


async def search_academic_profiles(
    query: str, max_results: int = 10
) -> List[SearchResult]:
    site_searches = [
        "site:*.edu/faculty",
        "site:*.edu/staff",
        "site:*.edu/people",
        "site:*.ac.uk/people",
        "site:*.ac.uk/staff",
        "site:researchgate.net/profile",
        "site:scholar.google.com/citations",
        "site:orcid.org",
        "site:webofscience.com/wos/author",
        "site:europepmc.org/authors",
    ]
    query = f"{query} (professor OR researcher OR faculty OR academic) {' OR '.join(site_searches)}"
    results = await ddgs_manager.run_search(_perform_text_search, query, max_results)
    return [
        SearchResultMapper.map_ddgs_text(r, SearchType.ACADEMIC_PROFILES)
        for r in results
    ]


# CUSTOM SEARCHES


async def search_pubmed(query: str, max_results: int = 20) -> List[SearchResult]:
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    params = {
        "term": query,
        "ac": "yes",
        "cauthor_id": "None",
        "user_filter": "",
        "schema": "none",
        "page": "1",
        "whatsnew": "None",
        "show_snippets": "on",
        "sort": "relevance",
        "sort_order": "desc",
        "format": "pubmed",
        "size": str(max_results),
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            text_data = await response.text()

    # Regex to capture PMID, Title, Background, and DOI from PubMed data
    pattern = re.compile(
        r"PMID-\s*(\d+).*?TI\s*-\s*(.*?)\s*AB\s*-\s*(.*?)\s*AID\s*-\s*(10\.\d{4,9}/\S+)\s*\[doi\]",
        re.DOTALL,
    )

    return [
        SearchResultMapper.map_pubmed(match) for match in pattern.findall(text_data)
    ]


async def search_zenodo(query: str, max_results: int = 10) -> List[SearchResult]:
    async with aiohttp.ClientSession() as session:
        try:
            params = {
                "q": query,
                "size": max_results,
                "type": "dataset",  # This might be the issue - let's make it optional
            }

            async with session.get(
                "https://zenodo.org/api/records", params=params
            ) as response:
                data = await response.json()

                # Debug the raw response

                if "hits" not in data:
                    logger.error(f"Unexpected Zenodo response structure: {data}")
                    return []

                results = []
                for item in data.get("hits", {}).get("hits", []):
                    try:
                        results.append(SearchResultMapper.map_zenodo(item))
                    except Exception as e:
                        logger.error(f"Error mapping Zenodo result: {str(e)}")
                        logger.debug(f"Problematic item data: {item}")
                        continue

                return results
        except Exception as e:
            logger.error(f"Zenodo search failed: {str(e)}")
            return []


async def search_openalex(query: str, max_results: int = 10) -> List[SearchResult]:
    # Configure pyalex properly

    pyalex_config.max_retries = 5
    pyalex_config.retry_backoff_factor = 0.1
    pyalex_config.retry_http_codes = [429, 500, 503]
    pyalex_config.email = os.getenv('ADMIN_EMAIL', 'user@example.com')

    try:
        # Set both per_page and n_max to max_results to get exactly what we want
        works = Works().search(query).paginate(per_page=max_results, n_max=max_results)
        results = []

        # We only need the first page since per_page=max_results
        for work in works:
            try:
                mapped_results = SearchResultMapper.map_openalex(work)
                if isinstance(mapped_results, list):
                    results.extend(mapped_results)
                else:
                    results.append(mapped_results)
                if len(results) >= max_results:
                    break
            except Exception as e:
                logger.error(f"Error mapping OpenAlex result: {str(e)}")
                logger.debug(f"Problematic work data: {work}")
                continue

        return results[:max_results]  # Ensure we don't return more than max_results
    except Exception as e:
        logger.error(f"OpenAlex search failed: {str(e)}")
        return []


async def search_science_general(
    query: str, max_results: int = max_results
) -> List[SearchResult]:
    """Combined scientific search across Zenodo and OpenAlex"""
    # Split max_results between the two sources
    per_source_results = max(2, max_results // 2)

    # Run both searches concurrently
    zenodo_task = search_zenodo(query, per_source_results)
    open_alex_task = search_openalex(query, per_source_results)

    results = await asyncio.gather(zenodo_task, open_alex_task)

    # Combine and interleave results
    combined_results = []
    zenodo_results, open_alex_results = results

    # Zip the results together, handling different lengths
    for i in range(max(len(zenodo_results), len(open_alex_results))):
        if i < len(zenodo_results):
            combined_results.append(zenodo_results[i])
        if i < len(open_alex_results):
            combined_results.append(open_alex_results[i])

    return combined_results[:max_results]


async def search_substack(query: str, max_results: int = 10) -> List[SearchResult]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://substack.com/api/v1/post/search?query={query}&page=0&numberFocused=3"
        ) as response:
            data = await response.json()
            combined = data.get("focused", []) + data.get("results", [])
            return [SearchResultMapper.map_substack(p) for p in combined[:max_results]]


async def search_arxiv(query: str, max_results: int = 10) -> List[SearchResult]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://export.arxiv.org/api/query?search_query=all:{query}&max_results={max_results}"
        ) as response:
            xml = await response.text()
            root = ET.fromstring(xml)
            
            results = []
            for entry in root.findall("{*}entry"):
                # Extract data from XML element
                entry_data = {
                    "title": entry.findtext("{*}title", "").strip(),
                    "id": entry.findtext("{*}id", ""),
                    "summary": entry.findtext("{*}summary", "").strip(),
                    "published": entry.findtext("{*}published", ""),
                    "authors": [author.findtext("{*}name", "") for author in entry.findall("{*}author")],
                    "categories": [cat.get("term", "") for cat in entry.findall("{*}category")],
                    "doi": None  # arXiv entries don't typically have DOIs in this feed
                }
                
                results.append(SearchResultMapper.map_arxiv(entry_data))
            
            return results


def expand_list(results: Union[List, Any]) -> List[Any]:
    """
    Recursively expand/flatten nested lists while preserving non-list objects.

    Args:
        results: A single result object or a list of results (potentially nested)

    Returns:
        List[Any]: Flattened list of result objects
    """
    if not isinstance(results, list):
        return [results]

    expanded = []
    for item in results:
        if isinstance(item, list):
            expanded.extend(expand_list(item))
        else:
            expanded.append(item)
    return expanded


# ********** DEEPER SEARCHES **********


async def search_clinical_trials(
    query: str,
    max_results: int = 10,
) -> List[SearchResult]:
    """
    Search ClinicalTrials.gov using pytrials.

    Args:
        query: Main search query
        max_results: Maximum number of results to return
        study_type: Filter by study type (e.g., "Interventional", "Observational")
        phase: Filter by trial phase (e.g., "Phase 1", "Phase 2")
        status: Filter by trial status (e.g., "Recruiting", "Completed")
        country: Filter by country
    """
    try:
        ct = ClinicalTrials()

        # Define comprehensive field list
        fields = [
            "NCTId",
            "BriefTitle",
            "NCTId",
            "Acronym",
            "OverallStatus",
            "BriefSummary",
            "HasResults",
            "Condition",
            "InterventionType",
            "InterventionName",
            "PrimaryOutcomeMeasure",
            "PrimaryOutcomeDescription",
            "PrimaryOutcomeTimeFrame",
            "SecondaryOutcomeMeasure",
            "SecondaryOutcomeDescription",
            "SecondaryOutcomeTimeFrame",
            "OtherOutcomeMeasure",
            "OtherOutcomeDescription",
            "OtherOutcomeTimeFrame",
            "LeadSponsorName",
            "CollaboratorName",
            "Sex",
            "MinimumAge",
            "MaximumAge",
            "StdAge",
            "Phase",
            "EnrollmentCount",
            "LeadSponsorClass",
            "StudyType",
            "DesignAllocation",
            "DesignInterventionModel",
            "DesignMasking",
            "DesignWhoMasked",
            "DesignPrimaryPurpose",
            "OrgStudyId",
            "SecondaryId",
            "StartDate",
            "PrimaryCompletionDate",
            "CompletionDate",
            "StudyFirstPostDate",
            "ResultsFirstSubmitDate",
            "LastUpdatePostDate",
            "LocationFacility",
            "LocationCity",
            "LocationState",
            "LocationZip",
            "LocationCountry",
            "NCTId",
            "LargeDocLabel",
            "LargeDocFilename",
        ]

        # Get study data
        response = ct.get_study_fields(
            search_expr=query, fields=fields, max_studies=max_results, fmt="json"
        )

        results = []
        studies = response.get("studies", {})

        for study in studies:
            try:
                # Parse dates
                protocolSection = study.get("protocolSection")
                result = SearchResult(
                    nct_id=protocolSection.get("identificationModule").get("nctId"),
                    title=protocolSection.get("identificationModule").get("briefTitle"),
                    condition=protocolSection.get("conditionsModule").get(
                        "conditions", []
                    ),
                    brief_summary=protocolSection.get("descriptionModule").get(
                        "briefSummary"
                    ),
                    detailed_description=protocolSection.get("descriptionModule").get(
                        "detailedDescription"
                    ),
                    study_type=protocolSection.get("designModule").get(
                        "studyType", [""]
                    )[0],
                    phase=protocolSection.get("designModule").get("phases", [""])[0]
                    if protocolSection.get("designModule").get("phases")
                    else None,
                    status=protocolSection.get("statusModule").get(
                        "overallStatus", [""]
                    )[0],
                    enrollment_count=int(
                        protocolSection.get("designModule")
                        .get("enrollmentInfo")
                        .get("count")
                    ),
                    locations=protocolSection.get("contactsLocationsModule").get(
                        "locations", []
                    ),
                    start_date=protocolSection.get("statusModule")
                    .get("startDateStruct")
                    .get("date"),
                    completion_date=protocolSection.get("statusModule")
                    .get("completionDateStruct")
                    .get("date"),
                    interventions=protocolSection.get("armsInterventionsModule").get(
                        "interventions", []
                    ),
                    primary_outcomes=protocolSection.get("outcomesModule").get(
                        "primaryOutcomes", []
                    ),
                    secondary_outcomes=protocolSection.get("outcomesModule").get(
                        "secondaryOutcomes", []
                    ),
                    eligibility_criteria=protocolSection.get("eligibilityModule").get(
                        "eligibilityCriteria", [""]
                    )[0],
                )
                results.append(result)

            except Exception as e:
                logger.error(
                    f"Error processing trial {study.get('NCTId', ['<unknown>'])[0]}: {str(e)}"
                )
                continue

        return results

    except Exception as e:
        logger.error(f"Error in clinical trials search: {str(e)}")
        return []


async def deep_search_pubmed(
    query: str, filters: Optional[List[PubMedFilterType]] = None, max_results: int = 20
) -> List[SearchResult]:
    """
    Perform an advanced PubMed search with specific filters.

    Args:
        query: The search query
        filters: List of PubMedFilterType enums to filter results
        max_results: Maximum number of results to return
    """
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"

    # Start with all our standard params
    params = {
        "term": query,
        "ac": "yes",
        "cauthor_id": "None",
        "user_filter": "",
        "schema": "none",
        "page": "1",
        "whatsnew": "None",
        "show_snippets": "on",
        "sort": "relevance",
        "sort_order": "desc",
        "format": "pubmed",
        "size": str(max_results),
    }

    # Add filters if provided
    if filters:
        # aiohttp will handle multiple values for the same key correctly
        params["filter"] = [f.value for f in filters]

    full_url = URL(base_url).with_query(params)
    logger.info(f"Full URL: {full_url}")

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            text_data = await response.text()

    # Rest of existing parsing logic...
    pattern = re.compile(
        r"PMID-\s*(\d+).*?TI\s*-\s*(.*?)\s*AB\s*-\s*(.*?)\s*AID\s*-\s*(10\.\d{4,9}/\S+)\s*\[doi\]",
        re.DOTALL,
    )

    pubmed_results = []
    matches = pattern.findall(text_data)

    for match in matches:
        pmid, title, background, doi = match
        href = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        pubmed_results.append(
            SearchResult(
                pmid=pmid, title=title, background=background, doi=doi, href=href
            )
        )

    return pubmed_results


# ********** END DEEPER SEARCHES **********


# Configure limits
MAX_CONCURRENT_SEARCHES = 5  # Adjust based on testing
RATE_LIMIT_DELAY = 1.0  # Seconds between searches
# STABLE SEARCH MAP - only includes reliable searches
stable_search_map = {
    SearchTypeStable.SCIENCE_GENERAL: search_openalex,    # OpenAlex API - always works
    SearchTypeStable.SCIENCE_ARXIV: search_arxiv,         # arXiv API - always works  
    SearchTypeStable.ZENODO: search_zenodo,               # Zenodo API - always works
}

# ALPHA SEARCH MAP - includes all searches (many broken due to rate limiting)
alpha_search_map = {
    # ✅ WORKING SEARCHES
    SearchType.SCIENCE_GENERAL: search_openalex,    # OpenAlex API - always works
    SearchType.SCIENCE_ARXIV: search_arxiv,         # arXiv API - always works  
    SearchType.ZENODO: search_zenodo,               # Zenodo API - always works
    
    # ❌ DISABLED - DDG dependent searches (rate limited)
    # SearchType.RESEARCHGATE: search_researchgate,     # DDG dependent - fails with rate limits
    # SearchType.SCIENCE_PUBMED: search_pubmed,         # DDG dependent - fails with rate limits
    # SearchType.INDEPENDENT_NEWS: search_substack,     # Often fails
    # SearchType.NEWS: search_news,                     # DDG dependent
    # SearchType.WEB: search_web,                       # DDG dependent
    # SearchType.SEMANTIC_SCHOLAR: search_semantic,     # DDG dependent
    # SearchType.PAPERITY: search_paperity,             # DDG dependent
    # SearchType.GOOGLE_SCHOLAR: search_scholar,        # DDG dependent
    # SearchType.ACADEMIC_SOURCES: search_academic_sources,  # DDG dependent
    # SearchType.OPEN_SCIENCE: search_open_science_sources,  # DDG dependent
    # SearchType.REFERENCE: search_reference,           # DDG dependent
    # SearchType.ACADEMIC_PROFILES: search_academic_profiles,  # DDG dependent
}


async def multi_search_interface(
    search_queries: List[Union[SearchQuery, SearchQueryAlpha]],
    max_results: int = 5,
    timeout: float = 15.0,
    rerank: bool = True,
    logger_callback=None,
) -> List[SearchResult]:
    """Execute multiple search types in parallel with progress tracking"""

    async def execute_search(search_query: Union[SearchQuery, SearchQueryAlpha]) -> List[SearchResult]:
        try:
            # Determine which search map to use
            if isinstance(search_query, SearchQuery):
                # Use stable search map for SearchQuery
                search_map = stable_search_map
                search_type = search_query.search_type
            else:
                # Use alpha search map for SearchQueryAlpha  
                search_map = alpha_search_map
                search_type = search_query.search_type
            
            if search_type not in search_map:
                if logger_callback:
                    logger_callback("invalid_search", f"❌ Invalid search type: {search_type.name}")
                return []

            results = await search_map[search_type](
                search_query.query, max_results
            )

            if not results:
                if logger_callback:
                    logger_callback("no_results", f"❌ No results found for {search_type.name} with query: '{search_query.query}'")
                return []
            if logger_callback:
                logger_callback("results_found", f"✅ Found {len(results)} results from {search_type.name} for: '{search_query.query}'")
            return results

        except Exception as e:
            error_msg = f"Error in {search_type.name} search for '{search_query.query}': {str(e)}"
            if logger_callback:
                logger_callback("search_error", f"❌ {error_msg}")
            logger.error(error_msg, exc_info=True)
            return []

    # Execute searches with timeout
    tasks = [execute_search(search_query) for search_query in search_queries]
    try:
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning("Search timed out")
        if logger_callback:
            logger_callback("timeout", f"❌ Search operations timed out after {timeout} seconds")
        return []

    # Flatten and deduplicate results
    flat_results = [r for sublist in results if sublist for r in sublist]

    if rerank and flat_results:
        flat_results = await rerank_results(
            " ".join(search_query.query for search_query in search_queries),
            flat_results,
        )

    if logger_callback:
        logger_callback("search_complete", f"✅ Search complete - found {len(flat_results)} unique results")

    return flat_results


async def rerank_results(
    query: str,
    results: List[SearchResult],
    fields: List[str] = None,
    max_tokens: int = 4000,
    encoding_name: str = "cl100k_base",  # OpenAI's default encoding
) -> List[SearchResult]:
    """
    Re-rank results and limit total tokens.

    Args:
        query: Original search query
        results: List of search results
        fields: List of fields to use for ranking
        max_tokens: Maximum total tokens to return
        encoding_name: Tokenizer encoding to use for counting

    Returns:
        List of re-ranked results within token limit
    """
    if not results:
        return results

    if fields is None:
        fields = ["title", "body", "abstract", "background"]

    # First, rerank all results
    def get_text(result):
        text_parts = []
        for field in fields:
            if field == "body":
                value = (
                    getattr(result, "body", None)
                    or getattr(result, "abstract", None)
                    or getattr(result, "background", None)
                )
            elif field == "abstract":
                value = (
                    getattr(result, "abstract", None)
                    or getattr(result, "body", None)
                    or getattr(result, "background", None)
                )
            else:
                value = getattr(result, field, None)

            if value:
                text_parts.append(str(value))

        return " ".join(text_parts)

    # Rerank using BM25
    tokenized_corpus = [get_text(result).lower().split() for result in results]
    tokenized_query = query.lower().split()
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenized_query)

    # Create list of tuples with scores and indices, then sort
    scored_indices = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    # Use indices to reorder results
    ranked_results = [results[idx] for idx, _ in scored_indices]

    # Now limit by tokens
    encoding = tiktoken.get_encoding(encoding_name)
    total_tokens = 0
    final_results = []

    for result in ranked_results:
        result_text = get_text(result)
        result_tokens = len(encoding.encode(result_text))

        if total_tokens + result_tokens <= max_tokens:
            final_results.append(result)
            total_tokens += result_tokens
        else:
            break

    return final_results


def title_similarity(title1: str, title2: str) -> float:
    """
    Calculate similarity between two titles using basic string matching.
    Returns a value between 0 (completely different) and 1 (identical).
    """
    # Remove common punctuation and convert to lowercase
    title1 = re.sub(r"[^\w\s]", "", title1.lower())
    title2 = re.sub(r"[^\w\s]", "", title2.lower())

    # Split into words
    words1 = set(title1.split())
    words2 = set(title2.split())

    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    return intersection / union if union > 0 else 0.0


async def search_openalex_by_topics(topic_ids: list, max_results: int = 10) -> List[SearchResult]:
    """
    Search OpenAlex for works tagged with any of the topic_ids using PyAlex.
    Args:
        topic_ids: List of OpenAlex topic IDs (e.g., ['C123456789', ...])
        max_results: Maximum number of results to return
    Returns:
        List[SearchResult]
    """
    if not topic_ids:
        return []
    filter_str = "|".join(topic_ids)
    works = Works().filter(**{"topics.id": filter_str}).paginate(per_page=max_results, n_max=max_results)
    results = []
    for work in works:
        try:
            mapped = SearchResultMapper.map_openalex(work)
            if isinstance(mapped, list):
                results.extend(mapped)
            else:
                results.append(mapped)
            if len(results) >= max_results:
                break
        except Exception as e:
            logger.error(f"Error mapping OpenAlex topic search result: {str(e)}")
            continue
    return results[:max_results]
