"""
Part D: Agent Orchestrator (Bonus)

ReAct agent with cloud cost optimization retrieval tool.
"""

import os
from typing import Annotated
from dotenv import load_dotenv
from langchain_core.tools import tool
# from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
import prompt
from retrieval_pipeline import RetrievalPipeline
from prompt import rag_prompt

load_dotenv()

# Initialize retrieval pipeline
retrieval_pipeline = RetrievalPipeline()


@tool
def retrieve_cloud_optimization_info(query: Annotated[str, "The cloud cost optimization question"]) -> str:
    """
    Retrieve information about cloud cost optimization from the knowledge base.
    
    Use this tool when users ask about:
    - AWS, Azure, or GCP cost optimization
    - Storage optimization (S3, Blob Storage, Cloud Storage)
    - Compute optimization (EC2, VMs, Compute Engine)
    - Cost reduction strategies
    - FinOps best practices
    """
    results = retrieval_pipeline.retrieve(query, top_k=3)
    
    context_parts = []
    for i, result in enumerate(results, 1):
        source = result['metadata']['source']
        provider = result['metadata']['provider']
        content = result['content'][:500]
        context_parts.append(f"[Source {i}: {source} - {provider}]\n{content}")
    
    return "\n\n".join(context_parts)


def create_agent():
    """Create ReAct agent with retrieval tool."""
    
    agent = create_react_agent(
        model="gpt-4.1",
        tools=[retrieve_cloud_optimization_info],
        prompt=rag_prompt.format()
    )
    
    return agent


def query_agent(user_query: str):
    """Query the agent and return response."""
    agent = create_agent()
    
    response = agent.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })
    
    return response["messages"][-1].content


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AGENT ORCHESTRATOR DEMO")
    print("=" * 60 + "\n")
    
    test_queries = [
        "How do I reduce S3 storage costs?",
        "What are Azure Spot VM savings?",
        "Hello, how are you?",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        answer = query_agent(query)
        print(f"Answer: {answer[:300]}...")