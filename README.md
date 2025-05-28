# SearchTheScience

![Search Success Rate](https://img.shields.io/badge/Search_Success_Rate-16.7%25-red)
![Working Searches](https://img.shields.io/badge/Working_Searches-3%2F18-red)
![Contributors Needed](https://img.shields.io/badge/Contributors-NEEDED-brightgreen)

A unified Python package for searching across scientific databases and sources. Designed for integration with LLMs and AI agents to provide comprehensive scientific research capabilities.

**⚠️ Currently only 3 out of 18 search types work reliably - we need your help to fix the rest!**

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
searchthescience = {git = "https://github.com/philmade/SearchTheScience.git"}
```

### For development
```bash
git clone https://github.com/philmade/SearchTheScience.git
cd SearchTheScience
pip install -e .
```

### From PyPI (coming soon)
```bash
pip install searchthescience
```

## Quick Start

### ✅ **Stable/Reliable Usage (Recommended)**

Use `SearchQuery` with `SearchTypeStable` for reliable, tested searches:

```python
import asyncio
from searchthescience import multi_search_interface, SearchQuery, SearchTypeStable

async def main():
    # Use only stable, working search types
    queries = [
        SearchQuery(search_type=SearchTypeStable.SCIENCE_GENERAL, query="machine learning in medicine"),
        SearchQuery(search_type=SearchTypeStable.SCIENCE_ARXIV, query="neural networks"),
        SearchQuery(search_type=SearchTypeStable.ZENODO, query="AI datasets")
    ]
    
    results = await multi_search_interface(queries, max_results=5, rerank=True)
    
    for result in results:
        print(f"Title: {result.title}")
        print(f"URL: {result.href}")
        print(f"Source: {result.source}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
```

### ⚠️ **Experimental/Alpha Usage**

Use `SearchQueryAlpha` with full `SearchType` for experimental access (many searches may fail):

```python
from searchthescience import SearchQueryAlpha, SearchType

# WARNING: Many of these search types don't work due to rate limiting
queries = [
    SearchQueryAlpha(search_type=SearchType.SCIENCE_PUBMED, query="cancer research"),  # May fail
    SearchQueryAlpha(search_type=SearchType.RESEARCHGATE, query="AI research"),       # May fail
]
```

### Basic Usage

```python
import asyncio
from searchthescience import multi_search_interface, SearchQuery, SearchType

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
from searchthescience import multi_search_interface, SearchQuery, SearchTypeStable

async def search_for_llm(user_query: str):
    """
    Search function designed for LLM integration.
    Returns formatted results ready for LLM consumption.
    """
    # Use stable search types only for reliability
    search_queries = [
        SearchQuery(search_type=SearchTypeStable.SCIENCE_GENERAL, query=user_query),
        SearchQuery(search_type=SearchTypeStable.SCIENCE_ARXIV, query=user_query),
        SearchQuery(search_type=SearchTypeStable.ZENODO, query=user_query),
    ]
    
    results = await multi_search_interface(
        search_queries=search_queries,
        max_results=3,
        rerank=True
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

### Pydantic AI Agent Example

```python
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import List
from searchthescience import multi_search_interface, SearchQuery, SearchTypeStable

class SearchTaskAndResults(BaseModel):
    results: List = []
    iterations: int = 0

# Create agent with search capabilities
search_agent = Agent(
    model='openai:gpt-4',
    deps_type=SearchTaskAndResults,
    system_prompt="""You are a research assistant that can search scientific literature.
    Use the execute_searches tool to find relevant papers for user questions."""
)

@search_agent.tool
async def execute_searches(
    ctx: RunContext[SearchTaskAndResults], queries: List[SearchQuery]
) -> str:
    """Execute scientific literature searches."""
    try:
        results = await multi_search_interface(
            search_queries=queries, max_results=5, rerank=True
        )
        valid_results = [r for r in results if not isinstance(r, Exception)]
        ctx.deps.results.extend(valid_results)
        ctx.deps.iterations += 1
        return f"✅ Found {len(valid_results)} results from {len(queries)} searches"
    except Exception as e:
        return f"❌ Search failed: {str(e)}"

# Usage
async def main():
    # Create search context
    search_context = SearchTaskAndResults()
    
    # Ask the agent to research
    response = await search_agent.run(
        "Find recent papers about CRISPR gene editing applications",
        deps=search_context
    )
    
    print(f"Agent response: {response.data}")
    print(f"Found {len(search_context.results)} papers")

if __name__ == "__main__":
    asyncio.run(main())
```

### Crossref Metadata Search

```python
import asyncio
from searchthescience import Metasearch

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

### ✅ **Stable Search Types (Always Work)**

```python
from searchthescience import SearchTypeStable

# Only 3 search types are currently stable and reliable:
SearchTypeStable.SCIENCE_GENERAL  # OpenAlex - comprehensive scientific papers
SearchTypeStable.SCIENCE_ARXIV    # arXiv - preprints and recent research  
SearchTypeStable.ZENODO           # Zenodo - datasets and research outputs
```

### ⚠️ **Experimental Search Types (Many Broken)**

```python
from searchthescience import SearchType

# 18 total search types exist, but most don't work due to rate limiting:
SearchType.SCIENCE_PUBMED       # ❌ Often fails - rate limited
SearchType.RESEARCHGATE         # ❌ Often fails - rate limited
SearchType.SEMANTIC_SCHOLAR     # ❌ Often fails - rate limited
SearchType.INDEPENDENT_NEWS     # ❌ Often fails - rate limited
SearchType.NEWS                 # ❌ Disabled - rate limited
SearchType.WEB                  # ❌ Disabled - rate limited
# ... 12+ more (see SearchType enum for full list)
```

**Current Status**: Only **3 out of 18** search types work reliably. We need contributors to fix the broken ones! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

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
from searchthescience import multi_search_interface, SearchQuery, SearchType

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

## 🤝 Contributing - We Need Your Help!

**SearchTheScience currently only has 3 working search types out of 18!** We desperately need contributors to fix the broken searches and add new ones.

### 🚨 **What's Broken & Why**

**Problem**: Most searches fail due to **DuckDuckGo rate limiting** (403/202 errors)

**Current Status**:
- ✅ **3 working**: OpenAlex, arXiv, Zenodo (direct APIs)
- ❌ **15+ broken**: PubMed, ResearchGate, Google Scholar, etc. (DDG dependent)

### 🛠️ **What We Need**

#### **High Priority Fixes:**

1. **🔬 PubMed Direct API** - Replace DDG scraping with [E-utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
2. **🎓 ResearchGate Alternative** - Find non-DDG way to search ResearchGate
3. **🧠 Semantic Scholar Direct** - Use [Semantic Scholar API](https://api.semanticscholar.org/)
4. **📰 News Sources** - Alternative to DDG news (maybe RSS feeds?)
5. **🌐 Web Search** - Alternative to DDG (Bing API, SerpAPI, etc.)

#### **Medium Priority:**

6. **🔍 Google Scholar** - Challenging due to bot detection
7. **📊 New Search Sources** - Add more scientific databases
8. **🔄 Proxy Support** - Better proxy rotation for DDG searches
9. **⚡ Rate Limiting** - Smart backoff strategies

### 🚀 **How to Contribute**

#### **1. Quick Start for Developers**

```bash
# Clone and setup
git clone https://github.com/philmade/SearchTheScience.git
cd SearchTheScience
pip install -e .

# See exactly what needs fixing
python show_broken_searches.py

# Test current state
python test_all_searches.py
```

**This will show you**: Current 16.7% success rate, which searches are broken, difficulty levels, and suggested APIs!

#### **2. Fix a Broken Search (Example: PubMed)**

```python
# File: searchthescience/search_functions.py

async def search_pubmed_direct(query: str, max_results: int = 10) -> List[SearchResult]:
    """Direct PubMed API instead of DDG scraping."""
    
    # Use E-utilities API instead of DuckDuckGo
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            data = await response.json()
            # Process results...
            return results

# Add to alpha_search_map:
alpha_search_map[SearchType.SCIENCE_PUBMED] = search_pubmed_direct

# Test it works, then move to stable_search_map!
```

#### **3. Test Your Changes**

```bash
# Test individual search
python -c "
import asyncio
from searchthescience.search_functions import search_pubmed_direct
results = asyncio.run(search_pubmed_direct('cancer research', 3))
print(f'✅ PubMed now works: {len(results)} results')
for r in results:
    print(f'  - {r.title}')
"

# Run full test suite
python test_all_searches.py
```

#### **4. Submit Pull Request**

1. **Fork** the repository
2. **Create branch**: `git checkout -b fix-pubmed-search`
3. **Make changes** to fix one search type
4. **Test thoroughly** - ensure it works consistently
5. **Update search maps** - add to `alpha_search_map`, then `stable_search_map` if reliable
6. **Submit PR** with title like "Fix PubMed search using direct E-utilities API"

### 📋 **Contribution Guidelines**

#### **🎯 Focus Areas (Pick One)**

| Search Type | Status | Difficulty | API Available |
|-------------|--------|------------|---------------|
| `SCIENCE_PUBMED` | ❌ Broken | Easy | ✅ [E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) |
| `SEMANTIC_SCHOLAR` | ❌ Broken | Easy | ✅ [API Docs](https://api.semanticscholar.org/) |
| `RESEARCHGATE` | ❌ Broken | Hard | ❌ No public API |
| `GOOGLE_SCHOLAR` | ❌ Broken | Very Hard | ❌ Bot detection |
| `NEWS` | ❌ Broken | Medium | ⚠️ Various RSS/APIs |
| `WEB` | ❌ Broken | Medium | ⚠️ Bing/SerpAPI (paid) |

#### **✅ Requirements for Acceptance**

1. **Works consistently** - No rate limiting or frequent failures
2. **Returns proper data** - Title, URL, description populated
3. **Handles errors gracefully** - Returns `[]` on failure, doesn't crash
4. **Includes tests** - Demonstrate it works with real queries
5. **Follows existing patterns** - Look at working searches as examples

#### **🚫 What We DON'T Want**

- ❌ More DuckDuckGo-dependent searches (they'll just break again)
- ❌ Paid API services without free tiers
- ❌ Searches that require user authentication
- ❌ Slow searches (>10 seconds typical response)

### 🆘 **Need Help?**

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/philmade/SearchTheScience/issues)
- **💡 Feature Ideas**: [GitHub Discussions](https://github.com/philmade/SearchTheScience/discussions) 
- **❓ Questions**: Tag `@philmade` in issues
- **📖 Detailed Guide**: See [CONTRIBUTING.md](CONTRIBUTING.md)

### 🏆 **Contributor Recognition**

Contributors who fix broken searches will be:
- **🎉 Listed in README** as core contributors
- **⭐ Credited in release notes**
- **🚀 Given maintainer access** for significant contributions

**Even fixing ONE search type would be incredibly valuable!** The package currently has only 16.7% of search types working - any improvement helps thousands of researchers.

### 💡 **Quick Win Ideas**

1. **Start small**: Pick `SCIENCE_PUBMED` - it has a well-documented free API
2. **Copy patterns**: Look at `search_openalex()` as a template for direct API calls
3. **Test extensively**: Use `python test_all_searches.py` to validate
4. **One PR per search**: Focus on one search type per pull request

**Let's make SearchTheScience the comprehensive scientific search tool it was meant to be!** 🔬✨

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.1.0
- Initial release
- Multi-source scientific search
- LLM integration support
- Pydantic data models
- Async support