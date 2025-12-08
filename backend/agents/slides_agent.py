"""
Slides Agent - Handles queries about lecture slides.

This agent:
1. Retrieves relevant slides from Pinecone
2. Generates responses referencing specific slides
3. Includes slide numbers and titles
4. Can use timestamp to find slides shown at specific times
"""

from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from services.pinecone_service import get_pinecone_service
from utils.prompts import SLIDES_AGENT_SYSTEM_PROMPT, format_context
from config import Config


def slides_agent_node(state: AgentState) -> Dict:
    """
    Slides agent node for LangGraph workflow.
    
    Retrieves and answers questions about lecture slides.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with response and slide references
    """
    print("[SLIDES] Retrieving slide information...")
    
    # Get Pinecone service
    pinecone_service = get_pinecone_service()
    
    # Use enriched query if available
    query = state.get("enriched_query") or state["current_query"]
    
    # Retrieve relevant slides
    namespaces = state.get("target_namespaces", [Config.NAMESPACE_SLIDES])
    
    # Query multiple namespaces if specified
    if len(namespaces) > 1:
        context_docs = pinecone_service.query_multiple_namespaces(
            query=query,
            namespaces=namespaces,
            top_k_per_namespace=3
        )
    else:
        context_docs = pinecone_service.query_namespace(
            query=query,
            namespace=Config.NAMESPACE_SLIDES,
            top_k=Config.TOP_K_RESULTS
        )
    
    # If timestamp is available, also get transcript context
    timestamp = state.get("timestamp")
    if timestamp is not None:
        transcript_docs = pinecone_service.query_with_timestamp(
            query=query,
            timestamp=timestamp,
            namespace=Config.NAMESPACE_TRANSCRIPT
        )
        context_docs.extend(transcript_docs[:2])  # Add top 2 transcript chunks
    
    print(f"   Retrieved {len(context_docs)} relevant documents")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=Config.LLM_MODEL,
        temperature=Config.LLM_TEMPERATURE,
        openai_api_key=Config.OPENAI_API_KEY,
        max_tokens=Config.LLM_MAX_TOKENS
    )
    
    # Format context
    formatted_context = format_context(context_docs)
    
    # Create prompt
    prompt = SLIDES_AGENT_SYSTEM_PROMPT.format(
        context=formatted_context,
        query=query
    )
    
    # Generate response
    messages = [SystemMessage(content=prompt)]
    response = llm.invoke(messages)
    answer = response.content.strip()
    
    # Extract slide references
    citations = []
    for doc in context_docs:
        metadata = doc.get("metadata", {})
        namespace = metadata.get("namespace", "")
        
        if namespace == "slides":
            citation = {
                "type": "slide",
                "slide_number": metadata.get("slide_number", "N/A"),
                "slide_title": metadata.get("slide_title", ""),
                "score": doc.get("score", 0.0)
            }
            citations.append(citation)
        elif namespace == "transcript":
            citation = {
                "type": "transcript",
                "start_time": metadata.get("start_time", 0),
                "end_time": metadata.get("end_time", 0),
                "score": doc.get("score", 0.0)
            }
            citations.append(citation)
    
    print(f"   Generated response with {len(citations)} references")
    
    # Update state
    return {
        "context": context_docs,
        "response": answer,
        "citations": citations,
        "agent_history": ["slides_agent"],
        "next_agent": None  # End of workflow
    }
