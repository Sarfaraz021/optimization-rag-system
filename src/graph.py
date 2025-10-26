import os
import sys
from typing import Annotated
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from retrieval_pipeline import RetrievalPipeline
from prompt import rag_prompt

load_dotenv()

# Initialize retrieval pipeline - EXACT copy from your agent_orchestrator.py
retrieval_pipeline = RetrievalPipeline()

# EXACT copy of your tool from agent_orchestrator.py
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

# Use gpt-4o-mini instead of gpt-4.1 (which doesn't exist)
model = ChatOpenAI(
    model="gpt-4.1",
    temperature=0,
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

# Create the LangGraph agent - equivalent to your create_agent() function
graph = create_react_agent(
    model=model,
    tools=[retrieve_cloud_optimization_info],
    prompt=rag_prompt.format()
)

# Add metadata for LangSmith
graph.name = "Cloud Cost Optimization Agent"
graph.description = "A ReAct agent that helps users optimize cloud costs using a comprehensive RAG pipeline"