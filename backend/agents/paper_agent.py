"""
Paper Agent - Handles queries about research papers.

This agent:
1. Retrieves relevant paper sections from Pinecone
2. Generates responses with proper citations
3. Includes paper metadata (title, authors, page numbers)
"""

from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from services.pinecone_service import get_pinecone_service
from utils.prompts import PAPER_AGENT_SYSTEM_PROMPT, format_context
from config import Config


def paper_agent_node(state: AgentState) -> Dict:
    """
    Paper agent node for LangGraph workflow.
    
    Retrieves and answers questions about research papers.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with response and citations
    """
    print("[PAPER] Retrieving research paper information...")
    
    # Get Pinecone service
    pinecone_service = get_pinecone_service()
    
    # Use enriched query if available
    query = state.get("enriched_query") or state["current_query"]
    
    # Retrieve relevant papers
    # Check if papers namespace is in target namespaces
    namespaces = state.get("target_namespaces", [])
    if Config.NAMESPACE_PAPERS not in namespaces:
        namespaces.append(Config.NAMESPACE_PAPERS)
    
    # Query Pinecone for papers
    context_docs = pinecone_service.query_namespace(
        query=query,
        namespace=Config.NAMESPACE_PAPERS,
        top_k=Config.TOP_K_RESULTS
    )
    
    print(f"   Retrieved {len(context_docs)} paper sections")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=Config.LLM_MODEL,
        temperature=Config.LLM_TEMPERATURE,
        openai_api_key=Config.OPENAI_API_KEY,
        max_tokens=Config.LLM_MAX_TOKENS # Changed from max_output_tokens to max_tokens for ChatOpenAI
    )
    
    # Format context
    formatted_context = format_context(context_docs)
    
    # Create prompt
    prompt = PAPER_AGENT_SYSTEM_PROMPT.format(
        context=formatted_context,
        query=query
    )
    
    # Generate response
    messages = [SystemMessage(content=prompt)]
    response = llm.invoke(messages)
    answer = response.content.strip()
    
    # Extract citations
    citations = []
    for doc in context_docs:
        metadata = doc.get("metadata", {})
        citation = {
            "type": "paper",
            "title": metadata.get("title", "Unknown Paper"),
            "page": metadata.get("page", "N/A"),
            "score": doc.get("score", 0.0)
        }
        citations.append(citation)
    
    print(f"   Generated response with {len(citations)} citations")
    
    # Update state
    return {
        "context": context_docs,
        "response": answer,
        "citations": citations,
        "agent_history": ["paper_agent"],
        "next_agent": None  # End of workflow
    }
