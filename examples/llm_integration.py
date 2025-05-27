#!/usr/bin/env python3
"""
LLM Integration example for SearchTheScience package.
This example shows how to integrate SearchTheScience with LLMs and AI agents.
"""

import asyncio
import sys
import os
from typing import List, Dict, Any

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from searchthescience import multi_search_interface, SearchQuery, SearchType, SearchResult


class SearchAgent:
    """
    Example LLM agent that uses SearchTheScience for scientific research.
    This demonstrates how to integrate the search functionality with AI systems.
    """
    
    def __init__(self):
        self.search_history: List[str] = []
        self.results_cache: Dict[str, List[SearchResult]] = {}
    
    async def research_question(self, question: str, max_results: int = 5) -> str:
        """
        Main research function that an LLM would call.
        
        Args:
            question: Research question from user
            max_results: Maximum results to return
            
        Returns:
            Formatted research results ready for LLM processing
        """
        print(f"🔍 Researching: '{question}'")
        
        # Store in history
        self.search_history.append(question)
        
        # Check cache first
        if question in self.results_cache:
            print("📁 Using cached results")
            results = self.results_cache[question]
        else:
            # Determine appropriate search strategies based on question
            search_queries = self._generate_search_queries(question)
            
            # Custom logger for LLM feedback
            def search_logger(action_type: str, message: str):
                print(f"  [{action_type}] {message}")
            
            # Execute searches
            results = await multi_search_interface(
                search_queries=search_queries,
                max_results=max_results,
                rerank=True,
                logger_callback=search_logger
            )
            
            # Cache results
            self.results_cache[question] = results
        
        # Format for LLM consumption
        return self._format_results_for_llm(question, results)
    
    def _generate_search_queries(self, question: str) -> List[SearchQuery]:
        """
        Generate appropriate search queries based on the research question.
        This is where an LLM would analyze the question and determine search strategy.
        """
        queries = []
        
        # Always search PubMed for medical/biological topics
        queries.append(SearchQuery(
            search_type=SearchType.SCIENCE_PUBMED,
            query=question
        ))
        
        # Check for specific keywords to determine additional sources
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['machine learning', 'ai', 'algorithm', 'neural', 'deep learning']):
            # Add arXiv for CS/ML topics
            queries.append(SearchQuery(
                search_type=SearchType.SCIENCE_ARXIV,
                query=question
            ))
        
        if any(word in question_lower for word in ['data', 'dataset', 'repository', 'software']):
            # Add Zenodo for datasets
            queries.append(SearchQuery(
                search_type=SearchType.ZENODO,
                query=question
            ))
        
        # Always add general scientific search
        queries.append(SearchQuery(
            search_type=SearchType.SCIENCE_GENERAL,
            query=question
        ))
        
        print(f"  Generated {len(queries)} search queries:")
        for i, query in enumerate(queries, 1):
            print(f"    {i}. {query.search_type.name}")
        
        return queries
    
    def _format_results_for_llm(self, question: str, results: List[SearchResult]) -> str:
        """
        Format search results in a way that's optimal for LLM consumption.
        This creates a structured, token-efficient summary.
        """
        if not results:
            return f"No research results found for: '{question}'"
        
        formatted_output = []
        formatted_output.append(f"# Research Results for: {question}")
        formatted_output.append(f"Found {len(results)} relevant sources:\n")
        
        for i, result in enumerate(results, 1):
            # Use the built-in markdown formatter
            formatted_output.append(result.to_markdown(index=i-1))
        
        # Add summary statistics
        sources = {}
        for result in results:
            source = result.source
            sources[source] = sources.get(source, 0) + 1
        
        formatted_output.append("\n## Source Summary")
        for source, count in sources.items():
            formatted_output.append(f"- {source}: {count} results")
        
        return "\n".join(formatted_output)
    
    def get_search_history(self) -> List[str]:
        """Return search history for the LLM to reference."""
        return self.search_history.copy()


async def example_llm_workflow():
    """
    Demonstrate a complete LLM workflow using SearchTheScience.
    This simulates how an AI agent would use the search functionality.
    """
    print("🤖 LLM Integration Example")
    print("=" * 50)
    
    # Create search agent
    agent = SearchAgent()
    
    # Simulate LLM research questions
    research_questions = [
        "What are the latest treatments for Alzheimer's disease?",
        "How does machine learning improve medical diagnosis accuracy?",
        "What datasets are available for cancer research?",
    ]
    
    for i, question in enumerate(research_questions, 1):
        print(f"\n📋 Research Task {i}")
        print("-" * 30)
        
        try:
            # This is what an LLM would call
            research_results = await agent.research_question(question, max_results=3)
            
            print("\n📊 Results formatted for LLM:")
            print("=" * 40)
            
            # Show first part of results (truncated for demo)
            lines = research_results.split('\n')
            for line in lines[:15]:  # Show first 15 lines
                print(line)
            
            if len(lines) > 15:
                print(f"... (truncated, {len(lines) - 15} more lines)")
            
            print("\n" + "=" * 40)
            
        except Exception as e:
            print(f"❌ Error during research: {e}")
    
    # Show search history
    print(f"\n📚 Search History: {len(agent.get_search_history())} queries")
    for i, query in enumerate(agent.get_search_history(), 1):
        print(f"  {i}. {query}")


async def pydantic_ai_example():
    """
    Example of how to integrate with pydantic-ai framework.
    """
    print("\n🔧 Pydantic AI Integration Pattern")
    print("=" * 50)
    
    # This shows the pattern for pydantic-ai integration
    print("Integration pattern:")
    print("""
# In your pydantic-ai agent:

from pydantic_ai import Agent
from search_the_science import multi_search_interface, SearchQuery, SearchType

async def scientific_search_tool(query: str, search_types: List[str] = None) -> str:
    \"\"\"Tool function for pydantic-ai agent\"\"\"
    
    # Convert string search types to SearchType enums
    if search_types is None:
        search_types = ['SCIENCE_PUBMED', 'SCIENCE_GENERAL']
    
    search_queries = [
        SearchQuery(
            search_type=getattr(SearchType, st),
            query=query
        )
        for st in search_types
    ]
    
    results = await multi_search_interface(
        search_queries=search_queries,
        max_results=5,
        rerank=True
    )
    
    # Format for LLM
    return '\\n\\n'.join(r.to_markdown(i) for i, r in enumerate(results))

# Create agent with search capability
agent = Agent(
    model='openai:gpt-4',
    tools=[scientific_search_tool]
)

# The agent can now perform scientific searches automatically
""")
    
    print("\nThe agent would then be able to:")
    print("• Search scientific literature automatically")
    print("• Choose appropriate databases based on context")
    print("• Format results for easy interpretation")
    print("• Integrate search results into its responses")


async def main():
    """Run LLM integration examples."""
    
    print("🚀 Starting LLM Integration Examples")
    print("This demonstrates how to use SearchTheScience with AI agents...\n")
    
    try:
        # Run LLM workflow example
        await example_llm_workflow()
        
        # Show pydantic-ai integration pattern
        await pydantic_ai_example()
        
        print("\n✅ LLM Integration examples completed!")
        print("\n💡 Key Integration Points:")
        print("- Use SearchAgent class as a template for LLM integration")
        print("- The research_question() method is perfect for LLM tool calls")
        print("- Results are pre-formatted for token efficiency")
        print("- Built-in caching reduces API calls")
        print("- Search history tracking for context")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("Check your internet connection and try again.")


if __name__ == "__main__":
    asyncio.run(main())