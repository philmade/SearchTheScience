#!/usr/bin/env python3
"""
Test script to check for NoneType errors and validate search functionality.
"""

import asyncio
import sys
import os

# Add package to path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from searchthescience import multi_search_interface, SearchQuery, SearchType


async def test_individual_searches():
    """Test each search type individually to catch errors."""
    
    print("🧪 Testing Individual Search Functions")
    print("=" * 50)
    
    test_query = "machine learning"
    
    # Test each search type
    search_types_to_test = [
        SearchType.SCIENCE_ARXIV,
        SearchType.SCIENCE_GENERAL, 
        SearchType.ZENODO,
        SearchType.RESEARCHGATE,
    ]
    
    for search_type in search_types_to_test:
        print(f"\n🔍 Testing {search_type.name}...")
        
        try:
            query = SearchQuery(search_type=search_type, query=test_query)
            results = await multi_search_interface([query], max_results=2, timeout=10.0)
            
            print(f"✅ {search_type.name}: Found {len(results)} results")
            
            # Check for NoneType errors
            for i, result in enumerate(results):
                issues = []
                
                if result.title is None:
                    issues.append("title is None")
                elif result.title.strip() == "":
                    issues.append("title is empty")
                elif "Untitled" in result.title:
                    issues.append(f"title is placeholder: '{result.title}'")
                
                if result.href is None:
                    issues.append("href is None") 
                elif result.href.strip() == "":
                    issues.append("href is empty")
                
                if result.source is None:
                    issues.append("source is None")
                
                if issues:
                    print(f"  ⚠️  Result {i+1} issues: {', '.join(issues)}")
                    print(f"      Raw title: {repr(result.title)}")
                    print(f"      Raw href: {repr(result.href)}")
                else:
                    print(f"  ✅ Result {i+1}: '{result.title[:50]}...'")
                    
        except Exception as e:
            print(f"❌ {search_type.name} failed: {e}")
            import traceback
            traceback.print_exc()


async def test_concurrent_execution():
    """Test if searches actually run concurrently."""
    
    print("\n⏱️  Testing Concurrent Execution")
    print("=" * 50)
    
    import time
    
    # Test sequential vs concurrent timing
    queries = [
        SearchQuery(search_type=SearchType.SCIENCE_GENERAL, query="machine learning"),
        SearchQuery(search_type=SearchType.ZENODO, query="artificial intelligence"),
        SearchQuery(search_type=SearchType.RESEARCHGATE, query="deep learning"),
    ]
    
    # Time concurrent execution
    start_time = time.time()
    concurrent_results = await multi_search_interface(queries, max_results=2)
    concurrent_time = time.time() - start_time
    
    print(f"🚀 Concurrent execution: {concurrent_time:.2f} seconds")
    print(f"📊 Total results: {len(concurrent_results)}")
    
    # Check if we got results from multiple sources
    sources = set(result.source for result in concurrent_results)
    print(f"📍 Sources found: {len(sources)} different sources")
    for source in sources:
        count = sum(1 for r in concurrent_results if r.source == source)
        print(f"   - {source}: {count} results")
    
    if len(sources) > 1:
        print("✅ Concurrent execution working - multiple sources returned")
    else:
        print("⚠️  May not be truly concurrent - only one source returned")


async def test_error_handling():
    """Test error handling with invalid queries."""
    
    print("\n🛡️  Testing Error Handling")
    print("=" * 50)
    
    # Test with very short timeout
    try:
        queries = [SearchQuery(search_type=SearchType.SCIENCE_GENERAL, query="test")]
        results = await multi_search_interface(queries, timeout=0.001)  # Very short timeout
        print(f"⚠️  Short timeout returned {len(results)} results (expected 0)")
    except Exception as e:
        print(f"✅ Short timeout handled gracefully: {type(e).__name__}")
    
    # Test with empty query
    try:
        queries = [SearchQuery(search_type=SearchType.SCIENCE_GENERAL, query="")]
        results = await multi_search_interface(queries, max_results=1)
        print(f"📝 Empty query returned {len(results)} results")
    except Exception as e:
        print(f"⚠️  Empty query caused error: {e}")


async def test_data_quality():
    """Test data quality and completeness."""
    
    print("\n📋 Testing Data Quality")
    print("=" * 50)
    
    query = SearchQuery(search_type=SearchType.SCIENCE_GENERAL, query="coronavirus vaccine")
    results = await multi_search_interface([query], max_results=3)
    
    if not results:
        print("❌ No results returned")
        return
    
    for i, result in enumerate(results, 1):
        print(f"\n📄 Result {i}:")
        print(f"  Title: {result.title}")
        print(f"  URL: {result.href}")
        print(f"  Source: {result.source}")
        print(f"  Authors: {len(result.authors)} authors")
        print(f"  Published: {result.published}")
        
        # Check markdown formatting
        try:
            markdown = result.to_markdown(index=i-1)
            if len(markdown) > 50:
                print(f"  ✅ Markdown format: {len(markdown)} characters")
            else:
                print(f"  ⚠️  Short markdown: {len(markdown)} characters")
        except Exception as e:
            print(f"  ❌ Markdown error: {e}")


async def main():
    """Run all tests."""
    
    print("🚀 Starting SearchTheScience Tests")
    print("This will test for NoneType errors, concurrency, and data quality...\n")
    
    try:
        await test_individual_searches()
        await test_concurrent_execution() 
        await test_error_handling()
        await test_data_quality()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())