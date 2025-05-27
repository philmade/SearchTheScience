# Contributing to SearchTheScience

We welcome contributions to improve SearchTheScience! This document explains how to contribute, especially to fix the many search sources that are currently broken.

## Current State

**✅ WORKING (3 search types):**
- `SCIENCE_GENERAL` (OpenAlex API) - Always works
- `SCIENCE_ARXIV` (arXiv API) - Always works  
- `ZENODO` (Zenodo API) - Always works

**❌ BROKEN/DISABLED (15+ search types):**
- `SCIENCE_PUBMED`, `RESEARCHGATE`, `SEMANTIC_SCHOLAR`, etc.
- Most fail due to DuckDuckGo rate limiting (403/202 errors)

## Architecture

### Search Types

- **`SearchTypeStable`** - Only includes working searches (used by default `SearchQuery`)
- **`SearchType`** - Full enum with all search types (used by experimental `SearchQueryAlpha`)

### Search Maps

- **`stable_search_map`** - Maps `SearchTypeStable` to working search functions
- **`alpha_search_map`** - Maps `SearchType` to all search functions (many broken)

## How to Contribute

### 1. Fix Existing Broken Searches

Many searches are broken due to rate limiting. We need alternatives:

**Option A: Direct API Access**
Replace DuckDuckGo-dependent searches with direct API calls:

```python
# Instead of: site:pubmed.ncbi.nlm.nih.gov via DDG
# Use: Direct PubMed E-utilities API
async def search_pubmed_direct(query: str, max_results: int = 10):
    # Use https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
    pass
```

**Option B: Alternative Search Services**
Use other search services that don't rate limit as heavily.

**Option C: Proxy/Rate Limiting Solutions**
Implement better proxy rotation or rate limiting strategies.

### 2. Add New Search Sources

We'd love to support more scientific databases:

```python
async def search_new_source(query: str, max_results: int = 10) -> List[SearchResult]:
    # Your implementation here
    pass

# Add to alpha_search_map:
alpha_search_map[SearchType.NEW_SOURCE] = search_new_source

# If reliable, also add to stable_search_map:
stable_search_map[SearchTypeStable.NEW_SOURCE] = search_new_source
```

### 3. Testing Requirements

All search functions must:

1. **Work reliably** - No rate limiting or frequent failures
2. **Return proper SearchResult objects** - With title, href, description, etc.
3. **Handle errors gracefully** - Return empty list on failure, not crash
4. **Be async** - Follow the `async def` pattern

Test your contributions:

```bash
# Test individual search
python -c "
import asyncio
from searchthescience.search_functions import your_new_search
results = asyncio.run(your_new_search('test query', 2))
print(f'Results: {len(results)}')
"

# Run comprehensive tests
python test_all_searches.py
```

### 4. Code Style

- Follow existing patterns in `search_functions.py`
- Use proper type hints
- Add docstrings
- Handle exceptions properly
- Use `SearchResultMapper` for consistent result formatting

### 5. Promotion Path

1. **Start in alpha_search_map** - Add your search to experimental `SearchType`
2. **Test thoroughly** - Ensure reliability over time
3. **Move to stable** - Once proven reliable, add to `SearchTypeStable` and `stable_search_map`

## Current Priority Areas

### High Priority: Fix Core Academic Sources

1. **PubMed** - Medical research (currently broken due to DDG rate limiting)
2. **ResearchGate** - Academic networking (broken)
3. **Semantic Scholar** - AI-powered academic search (broken)

### Medium Priority: News and General Sources

4. **General Web Search** - Without DDG dependency
5. **News Sources** - Alternative to DDG news
6. **Independent News** - Fix Substack search

### Low Priority: Specialized Sources

7. **Google Scholar** - Academic citations (difficult due to bot detection)
8. **Reference Sources** - Government/educational sites
9. **Academic Profiles** - Researcher discovery

## Development Setup

```bash
git clone https://github.com/philmade/SearchTheScience.git
cd SearchTheScience
pip install -e .

# Run tests
python test_all_searches.py
python examples/basic_search.py
```

## Pull Request Guidelines

1. **Focus on reliability** - Working searches are better than feature-rich broken ones
2. **Include tests** - Demonstrate your search works with real queries
3. **Update documentation** - Add your search type to appropriate enums
4. **Small, focused PRs** - One search source per PR is ideal

## Getting Help

- **Issues**: Report bugs or ask questions in GitHub issues
- **Discussions**: Use GitHub discussions for broader topics
- **Code questions**: Reference existing working searches as examples

## Search Function Template

```python
async def search_your_source(query: str, max_results: int = 10) -> List[SearchResult]:
    """
    Search [Your Source] for academic papers.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of SearchResult objects
    """
    try:
        # Your search implementation
        results = []
        
        # Make API calls, parse responses, etc.
        # ...
        
        # Convert to SearchResult objects
        for raw_result in raw_results:
            result = SearchResultMapper.map_your_source(raw_result)
            results.append(result)
            
        return results[:max_results]
        
    except Exception as e:
        logger.error(f"Your source search failed: {e}")
        return []  # Always return empty list on failure
```

Thank you for helping make SearchTheScience more comprehensive and reliable! 🔬