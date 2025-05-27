#!/usr/bin/env python3
"""
Comprehensive test of ALL search types to see which work vs. which are disabled.
"""

import asyncio
import sys
import os

# Add package to path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from searchthescience import multi_search_interface, SearchQuery, SearchType


async def test_all_search_types():
    """Test every SearchType to see which are enabled vs disabled."""
    
    print("🔍 Testing ALL Search Types")
    print("=" * 60)
    
    # Get all SearchType values
    all_search_types = list(SearchType)
    
    print(f"📊 Found {len(all_search_types)} SearchType options:")
    for st in all_search_types:
        print(f"   - {st.name}")
    
    print(f"\n🧪 Testing each search type individually...\n")
    
    enabled_searches = []
    disabled_searches = []
    broken_searches = []
    
    test_query = "machine learning"
    
    for search_type in all_search_types:
        print(f"🔍 Testing {search_type.name}...", end=" ")
        
        try:
            query = SearchQuery(search_type=search_type, query=test_query)
            results = await multi_search_interface([query], max_results=1, timeout=5.0)
            
            if len(results) > 0:
                print(f"✅ WORKS - {len(results)} result(s)")
                enabled_searches.append(search_type.name)
                
                # Quick quality check
                result = results[0]
                issues = []
                if not result.title or "Untitled" in result.title:
                    issues.append("bad title")
                if not result.href:
                    issues.append("no URL")
                    
                if issues:
                    print(f"    ⚠️  Issues: {', '.join(issues)}")
                    
            else:
                print("❌ NO RESULTS")
                disabled_searches.append(search_type.name)
                
        except Exception as e:
            if "not in search_map" in str(e) or "Invalid search type" in str(e):
                print("❌ DISABLED (not in search_map)")
                disabled_searches.append(search_type.name)
            else:
                print(f"💥 ERROR: {e}")
                broken_searches.append((search_type.name, str(e)))
    
    # Summary
    print(f"\n📈 SUMMARY")
    print("=" * 60)
    print(f"✅ WORKING SEARCHES ({len(enabled_searches)}):")
    for search in enabled_searches:
        print(f"   - {search}")
    
    print(f"\n❌ DISABLED SEARCHES ({len(disabled_searches)}):")
    for search in disabled_searches:
        print(f"   - {search}")
    
    if broken_searches:
        print(f"\n💥 BROKEN SEARCHES ({len(broken_searches)}):")
        for search, error in broken_searches:
            print(f"   - {search}: {error}")
    
    print(f"\n📊 STATS:")
    print(f"   Working: {len(enabled_searches)}/{len(all_search_types)} ({len(enabled_searches)/len(all_search_types)*100:.1f}%)")
    print(f"   Disabled: {len(disabled_searches)}")
    print(f"   Broken: {len(broken_searches)}")


async def test_quality_of_enabled_searches():
    """Test the quality of enabled searches more thoroughly."""
    
    print(f"\n🔬 QUALITY TEST of Working Searches")
    print("=" * 60)
    
    # Get working searches from search_map
    from searchthescience.search_functions import search_map
    enabled_types = list(search_map.keys())
    
    test_queries = [
        "artificial intelligence",
        "climate change", 
        "coronavirus vaccine"
    ]
    
    for query_text in test_queries:
        print(f"\n🔍 Testing query: '{query_text}'")
        print("-" * 40)
        
        queries = [SearchQuery(search_type=st, query=query_text) for st in enabled_types]
        
        try:
            results = await multi_search_interface(queries, max_results=2, timeout=10.0)
            
            print(f"📊 Total results: {len(results)}")
            
            # Group by source
            by_source = {}
            for result in results:
                source = result.source
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(result)
            
            print(f"📍 Sources: {len(by_source)}")
            for source, source_results in by_source.items():
                print(f"   - {source}: {len(source_results)} results")
                
                # Show first result quality
                if source_results:
                    r = source_results[0]
                    quality_score = 0
                    if r.title and len(r.title.strip()) > 10:
                        quality_score += 1
                    if r.href and r.href.startswith('http'):
                        quality_score += 1
                    if r.authors:
                        quality_score += 1
                    if r.published:
                        quality_score += 1
                    
                    print(f"     Quality: {quality_score}/4 - '{r.title[:50]}...'")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run comprehensive search tests."""
    
    print("🚀 Comprehensive Search Type Testing")
    print("This will test EVERY search type to see what works...\n")
    
    await test_all_search_types()
    await test_quality_of_enabled_searches()
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("- Enable more search types by uncommenting them in search_map")
    print("- Fix any broken search implementations")
    print("- Consider removing non-working SearchType enums to avoid confusion")


if __name__ == "__main__":
    asyncio.run(main())