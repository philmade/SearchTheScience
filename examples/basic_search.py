#!/usr/bin/env python3
"""
Basic usage example of SearchTheScience package.
This example demonstrates how to perform simple searches across multiple scientific databases.
"""

import asyncio
import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from searchthescience import multi_search_interface, SearchQuery, SearchType


async def basic_search_example():
    """Demonstrate basic search functionality."""
    
    print("🔬 SearchTheScience - Basic Search Example")
    print("=" * 50)
    
    # Define search queries for different databases
    queries = [
        SearchQuery(
            search_type=SearchType.SCIENCE_PUBMED, 
            query="machine learning in medical diagnosis"
        ),
        SearchQuery(
            search_type=SearchType.SCIENCE_ARXIV, 
            query="deep learning healthcare"
        ),
        SearchQuery(
            search_type=SearchType.SCIENCE_GENERAL, 
            query="AI medical imaging"
        ),
    ]
    
    print(f"Searching across {len(queries)} databases...")
    print("Queries:")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query.search_type.name}: '{query.query}'")
    print()
    
    try:
        # Execute searches
        results = await multi_search_interface(
            search_queries=queries,
            max_results=3,  # Limit results per database
            rerank=True,    # Enable smart ranking
            timeout=30.0    # 30 second timeout
        )
        
        # Display results
        print(f"✅ Found {len(results)} total results")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"\n📄 Result {i}:")
            print(f"Title: {result.title}")
            print(f"Source: {result.source} ({result.result_type.name})")
            print(f"URL: {result.href}")
            
            if result.authors:
                authors = ", ".join(result.authors[:3])
                if len(result.authors) > 3:
                    authors += " et al."
                print(f"Authors: {authors}")
            
            if result.published:
                print(f"Published: {result.published}")
            
            if result.description:
                # Truncate description for display
                desc = result.description[:200] + "..." if len(result.description) > 200 else result.description
                print(f"Description: {desc}")
            
            print("-" * 30)
        
        # Show markdown format example
        if results:
            print("\n📝 Markdown format (for LLM consumption):")
            print("=" * 50)
            print(results[0].to_markdown(index=0))
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return False
    
    return True


async def search_specific_topic():
    """Search for a specific scientific topic."""
    
    print("\n🎯 Targeted Search Example")
    print("=" * 50)
    
    topic = "CRISPR gene editing applications"
    print(f"Searching for: '{topic}'")
    
    # Focus on high-quality scientific sources
    queries = [
        SearchQuery(search_type=SearchType.SCIENCE_PUBMED, query=topic),
        SearchQuery(search_type=SearchType.SCIENCE_GENERAL, query=topic),
        SearchQuery(search_type=SearchType.ZENODO, query=topic),
    ]
    
    try:
        results = await multi_search_interface(
            search_queries=queries,
            max_results=2,
            rerank=True
        )
        
        print(f"Found {len(results)} results:")
        
        for result in results:
            print(f"\n• {result.title}")
            print(f"  Source: {result.source}")
            if result.doi:
                print(f"  DOI: {result.doi}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run all examples."""
    
    print("🚀 Starting SearchTheScience Examples")
    print("This may take a moment as we search multiple databases...\n")
    
    # Run basic search example
    success1 = await basic_search_example()
    
    # Run targeted search example  
    success2 = await search_specific_topic()
    
    if success1 and success2:
        print("\n✅ All examples completed successfully!")
        print("\n💡 Tips:")
        print("- Use environment variable PROXY_AUTH if you need proxy support")
        print("- Set ADMIN_EMAIL for better OpenAlex API rate limits")
        print("- Adjust max_results based on your needs")
        print("- Enable rerank=True for better result quality")
    else:
        print("\n❌ Some examples failed. Check your internet connection and try again.")


if __name__ == "__main__":
    asyncio.run(main())