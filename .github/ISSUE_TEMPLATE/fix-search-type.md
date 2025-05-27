---
name: Fix Broken Search Type
about: Help fix one of the 15+ broken search types
title: 'Fix [SEARCH_TYPE_NAME] search'
labels: 'good first issue, help wanted, search-fix'
assignees: ''

---

## 🔬 Fix a Broken Search Type

**Search Type to Fix**: [e.g. SCIENCE_PUBMED, RESEARCHGATE, etc.]

### Current Problem
- ❌ This search type currently fails due to DuckDuckGo rate limiting
- ❌ Returns no results or throws errors
- ❌ Not included in stable_search_map

### Solution Needed
- ✅ Replace DDG dependency with direct API calls
- ✅ Return proper SearchResult objects
- ✅ Handle errors gracefully
- ✅ Add to alpha_search_map (and stable_search_map if reliable)

### Suggested Approach
**For SCIENCE_PUBMED**: Use [NCBI E-utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
**For SEMANTIC_SCHOLAR**: Use [Semantic Scholar API](https://api.semanticscholar.org/)
**For others**: Research available APIs or alternative approaches

### Resources
- 📖 [Contributing Guide](../CONTRIBUTING.md)
- 🔍 Look at working examples: `search_openalex()`, `search_arxiv()`, `search_zenodo()`
- 🧪 Test with: `python test_all_searches.py`

### Success Criteria
- [ ] Search returns results for test queries
- [ ] No rate limiting or frequent failures  
- [ ] Proper SearchResult objects with title, href, description
- [ ] Added to appropriate search_map
- [ ] Tests pass

**This is a great first contribution!** Even fixing ONE search type would help thousands of researchers.