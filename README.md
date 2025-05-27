# SearchTheScience

A unified Python package for searching across scientific databases and sources. Designed for integration with LLMs and AI agents to provide comprehensive scientific research capabilities.

## Features

- **Multi-source search**: Search across PubMed, arXiv, OpenAlex, Zenodo, ResearchGate, and more
- **Unified interface**: Single API for all scientific databases
- **LLM-friendly**: Designed for easy integration with AI agents and language models
- **Async support**: Full asynchronous support for high-performance applications
- **Smart ranking**: Built-in result ranking and deduplication
- **Pydantic models**: Type-safe data models for all results

## Installation

### Using pip (recommended)
```bash
pip install git+https://github.com/philmade/SearchTheScience.git
```

### Using uv (fastest)
```bash
uv pip install git+https://github.com/philmade/SearchTheScience.git
```

### Using Poetry
```bash
poetry add git+https://github.com/philmade/SearchTheScience.git
```

### In requirements.txt
```
git+https://github.com/philmade/SearchTheScience.git
```

### In pyproject.toml (Poetry)
```toml
[tool.poetry.dependencies]
searchthescience = {git = "https://github.com/philmade/searchthescience.git"}
```

### For development
```bash
git clone https://github.com/philmade/searchthescience.git
cd searchthescience
pip install -e .
```

### From PyPI (coming soon)
```bash
pip install searchthescience
```

## Quick Start

### Basic Usage

```python
import asyncio
from search_the_science import multi_search_interface, SearchQuery, SearchType

async def main():
    # Define your searches
    queries = [
        SearchQuery(search_type=SearchType.SCIENCE_PUBMED, query="machine learning in medicine"),
        SearchQuery(search_type=SearchType.SCIENCE_ARXIV, query="neural networks"),
        SearchQuery(search_type=SearchType.SCIENCE_GENERAL, query="artificial intelligence healthcare")
    ]
    
    # Execute parallel searches
    results = await multi_search_interface(
        search_queries=queries,
        max_results=5,
        rerank=True
    )
    
    # Process results
    for result in results:
        print(f"Title: {result.title}")
        print(f"URL: {result.href}")
        print(f"Source: {result.source}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
```

### LLM Integration Example

```python
import asyncio
from search_the_science import multi_search_interface, SearchQuery, SearchType

async def search_for_llm(user_query: str):
    """
    Search function designed for LLM integration.
    Returns formatted results ready for LLM consumption.
    """
    # Determine appropriate search types based on query
    search_queries = [
        SearchQuery(search_type=SearchType.SCIENCE_PUBMED, query=user_query),
        SearchQuery(search_type=SearchType.SCIENCE_GENERAL, query=user_query),
    ]
    
    # Custom logger for LLM feedback
    def log_callback(action_type: str, message: str):
        print(f"[{action_type}] {message}")
    
    results = await multi_search_interface(
        search_queries=search_queries,
        max_results=3,
        rerank=True,
        logger_callback=log_callback
    )
    
    # Format results for LLM
    formatted_results = []
    for i, result in enumerate(results):
        formatted_results.append(result.to_markdown(index=i))
    
    return "\\n\\n".join(formatted_results)

# Example usage
async def main():
    user_question = "What are the latest treatments for Alzheimer's disease?"
    search_results = await search_for_llm(user_question)
    print(search_results)

if __name__ == "__main__":
    asyncio.run(main())
```

### Crossref Metadata Search

```python
import asyncio
from search_the_science import Metasearch

async def main():
    metasearch = Metasearch()
    
    # Search by title
    papers = await metasearch.search_by_title("CRISPR gene editing", limit=3)
    
    # Search by DOI
    paper = await metasearch.search_by_doi("10.1038/s41586-021-03819-2")
    
    # Search by author
    author_papers = await metasearch.search_by_author("Jennifer Doudna", limit=5)
    
    print(f"Found {len(papers)} papers")

if __name__ == "__main__":
    asyncio.run(main())
```

## Available Search Types

```python
from search_the_science import SearchType

# Scientific databases
SearchType.SCIENCE_PUBMED       # PubMed medical research
SearchType.SCIENCE_ARXIV        # arXiv preprints
SearchType.SCIENCE_GENERAL      # OpenAlex (all fields)
SearchType.ZENODO              # Zenodo datasets and papers

# Academic sources
SearchType.RESEARCHGATE        # ResearchGate
SearchType.SEMANTIC_SCHOLAR    # Semantic Scholar
SearchType.PAPERITY           # Open access papers
SearchType.GOOGLE_SCHOLAR     # Google Scholar

# News and independent sources
SearchType.INDEPENDENT_NEWS    # Substack, newsletters
SearchType.NEWS               # Major news outlets

# Reference materials
SearchType.REFERENCE          # Government, educational sources
SearchType.ACADEMIC_PROFILES  # Researcher profiles
```

## Configuration

### Environment Variables

Optional configuration via environment variables:

```bash
# Optional proxy configuration
export PROXY_AUTH="philmade:password"

# Optional email for OpenAlex API (recommended for higher rate limits)
export ADMIN_EMAIL="your-email@example.com"
```

### Search Parameters

```python
await multi_search_interface(
    search_queries=queries,
    max_results=10,          # Results per search type
    timeout=30.0,           # Timeout in seconds
    rerank=True,            # Enable BM25 reranking
    logger_callback=None    # Optional logging callback
)
```

## Pydantic AI Compatibility

This package is designed to work seamlessly with pydantic-ai:

```python
from pydantic_ai import Agent
from search_the_science import multi_search_interface, SearchQuery, SearchType

# Create a pydantic-ai agent with search capabilities
agent = Agent(
    model='openai:gpt-4',
    tools=[multi_search_interface]
)

# The agent can now use scientific search in its responses
```

## Data Models

All results use type-safe Pydantic models:

```python
class SearchResult(BaseModel):
    result_type: SearchType
    title: Optional[str]
    href: str
    description: Optional[str] = None
    published: Optional[Union[datetime, str]] = None
    authors: List[str] = []
    source: str
    doi: Optional[str] = None
    additional_fields: Dict[str, Any] = Field(default_factory=dict)
    
    def to_markdown(self, index: Optional[int] = None) -> str:
        # Returns formatted markdown for LLM consumption
        pass
```

## Error Handling

The package includes robust error handling:

- Automatic retries for rate limits
- Graceful fallbacks for failed searches
- Timeout protection for slow APIs
- Detailed logging for debugging

## Dependencies

- `pydantic>=2.0.0` - Data validation and settings management
- `aiohttp>=3.8.0` - Async HTTP client
- `duckduckgo-search>=3.0.0` - Web search functionality
- `habanero>=1.2.0` - Crossref API client
- `pyalex>=0.12.0` - OpenAlex API client
- `pytrials>=0.1.0` - Clinical trials search
- `rank-bm25>=0.2.0` - Result ranking
- `tiktoken>=0.4.0` - Token counting for LLMs
- `loguru>=0.7.0` - Logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.1.0
- Initial release
- Multi-source scientific search
- LLM integration support
- Pydantic data models
- Async support