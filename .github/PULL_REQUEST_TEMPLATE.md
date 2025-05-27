# Fix Search Type: [Search Type Name]

## 🎯 What This Fixes
- **Search Type**: `SearchType.[SEARCH_TYPE_NAME]`
- **Problem**: [Describe what was broken - usually DDG rate limiting]
- **Solution**: [Describe your approach - direct API, alternative service, etc.]

## ✅ Changes Made
- [ ] Replaced DDG dependency with [API/service name]
- [ ] Added new search function: `search_[name]()`
- [ ] Updated search maps (alpha_search_map, stable_search_map if reliable)
- [ ] Added proper error handling
- [ ] Returns valid SearchResult objects

## 🧪 Testing
**Test Results**:
```
# Paste output from test commands here
python -c "
import asyncio
from searchthescience.search_functions import search_[your_function]
results = asyncio.run(search_[your_function]('test query', 3))
print(f'Results: {len(results)}')
for r in results:
    print(f'  - {r.title}')
"
```

**Full Test Suite**:
- [ ] `python test_all_searches.py` passes
- [ ] No rate limiting errors
- [ ] Consistent results across multiple test runs

## 📊 Before/After
**Before**: ❌ [Search type] returned 0 results due to rate limiting
**After**: ✅ [Search type] returns [X] results consistently

## 🔗 API Documentation
**API Used**: [Link to API docs if applicable]
**Rate Limits**: [Mention any rate limits or usage restrictions]
**Free Tier**: [Confirm this uses free/public APIs]

## ♻️ Breaking Changes
- [ ] No breaking changes
- [ ] Breaking changes (explain below)

## 📝 Additional Notes
[Any additional context, edge cases, or future improvements]

---

**Checklist**:
- [ ] Tested with multiple different queries
- [ ] Function handles errors gracefully (returns `[]`, doesn't crash)  
- [ ] Follows existing code patterns
- [ ] No new dependencies added (or justified if added)
- [ ] Results include proper title, href, description
- [ ] Added to appropriate search map(s)