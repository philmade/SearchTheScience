#!/usr/bin/env python3
"""
Quick script to show developers exactly what search types need fixing.
Run this to see the current status and pick something to work on!
"""

import sys
import os

# Add package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_status():
    """Show current search type status for contributors."""
    
    from searchthescience import SearchType, SearchTypeStable
    from searchthescience.search_functions import stable_search_map, alpha_search_map
    
    print("🔬 SearchTheScience - Current Status")
    print("=" * 60)
    
    # Count stats
    total_types = len(list(SearchType))
    stable_types = len(list(SearchTypeStable))
    alpha_working = len(alpha_search_map)
    
    print(f"📊 STATS:")
    print(f"   Total search types defined: {total_types}")
    print(f"   Stable (always work): {stable_types}")
    print(f"   Alpha (experimental): {alpha_working}")
    print(f"   Broken/disabled: {total_types - alpha_working}")
    print(f"   Success rate: {stable_types/total_types*100:.1f}%")
    
    print(f"\n✅ WORKING STABLE SEARCHES ({stable_types}):")
    for search_type in SearchTypeStable:
        print(f"   ✅ {search_type.name}")
    
    print(f"\n⚠️  WORKING ALPHA SEARCHES ({alpha_working - stable_types}):")
    for search_type, func in alpha_search_map.items():
        if search_type.name not in [st.name.replace('_STABLE', '') for st in SearchTypeStable]:
            # This is an alpha-only search
            print(f"   ⚠️  {search_type.name}")
    
    print(f"\n❌ BROKEN/DISABLED SEARCHES ({total_types - alpha_working}):")
    broken_searches = []
    for search_type in SearchType:
        if search_type not in alpha_search_map:
            broken_searches.append(search_type)
            
    # Show broken searches with suggested APIs
    api_suggestions = {
        'SCIENCE_PUBMED': 'E-utilities API (https://www.ncbi.nlm.nih.gov/books/NBK25501/)',
        'SEMANTIC_SCHOLAR': 'Semantic Scholar API (https://api.semanticscholar.org/)',
        'RESEARCHGATE': 'No public API - scraping alternative needed',
        'GOOGLE_SCHOLAR': 'No public API - very difficult',
        'NEWS': 'RSS feeds or news APIs',
        'WEB': 'Bing API or SerpAPI (paid)',
        'INDEPENDENT_NEWS': 'Direct RSS/API calls',
        'PAPERITY': 'Check if Paperity has API',
        'ACADEMIC_SOURCES': 'Combination of working APIs',
        'OPEN_SCIENCE': 'Combine multiple open access APIs',
        'REFERENCE': 'Government/edu site APIs',
        'ACADEMIC_PROFILES': 'ORCID API + others',
        'SCIENCE_BIORXIV': 'bioRxiv API',
        'PDF': 'PDF search services',
        'ADVANCED': 'Generic advanced search',
    }
    
    for search_type in broken_searches:
        suggestion = api_suggestions.get(search_type.name, 'Research available APIs')
        difficulty = "🟢 Easy" if search_type.name in ['SCIENCE_PUBMED', 'SEMANTIC_SCHOLAR'] else \
                    "🟡 Medium" if search_type.name in ['NEWS', 'WEB', 'INDEPENDENT_NEWS'] else \
                    "🔴 Hard"
        
        print(f"   ❌ {search_type.name:<20} {difficulty:<12} → {suggestion}")
    
    print(f"\n🚀 QUICK START FOR CONTRIBUTORS:")
    print(f"   1. Pick an Easy (🟢) search type from above")
    print(f"   2. git clone https://github.com/philmade/SearchTheScience.git")
    print(f"   3. Look at search_openalex() as template")
    print(f"   4. Replace DDG calls with direct API calls")
    print(f"   5. Test with: python test_all_searches.py")
    print(f"   6. Submit PR!")
    
    print(f"\n🏆 CONTRIBUTOR IMPACT:")
    print(f"   Fixing just ONE search type would improve success rate to {(stable_types+1)/total_types*100:.1f}%!")
    print(f"   Even small contributions help thousands of researchers!")
    
    print(f"\n📚 RESOURCES:")
    print(f"   📖 CONTRIBUTING.md - Detailed guide")
    print(f"   🧪 test_all_searches.py - Test suite")
    print(f"   💬 GitHub Issues - Ask questions")
    print(f"   🔗 https://github.com/philmade/SearchTheScience")


if __name__ == "__main__":
    show_status()