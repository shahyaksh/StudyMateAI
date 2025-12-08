"""
State schema for the multi-agent system.
Defines the shared state that flows through all agents in the LangGraph workflow.
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    Shared state for all agents in the workflow.
    
    This state is passed between agents and updated as the workflow progresses.
    """
    
    # Conversation context
    messages: Annotated[List[BaseMessage], operator.add]  # Full conversation history
    current_query: str  # User's current question
    enriched_query: Optional[str]  # Query enhanced with context by metadata agent
    
    # Temporal context
    timestamp: Optional[float]  # Current video timestamp in seconds
    lecture_id: Optional[str]  # Identifier for the current lecture
    
    # Intent and routing
    intent: Optional[str]  # Detected intent: "paper", "slide", "quiz", "flashcard", "general"
    target_namespaces: Optional[List[str]]  # Pinecone namespaces to query
    
    # Retrieved context
    context: Optional[List[Dict]]  # Retrieved documents from Pinecone
    
    # Response generation
    response: Optional[str]  # Final response to user
    citations: Optional[List[Dict]]  # Citations/references for the response
    
    # Metadata
    metadata: Optional[Dict]  # Additional metadata (slide numbers, paper titles, etc.)
    
    # Agent tracking
    next_agent: Optional[str]  # Which agent to route to next
    agent_history: Annotated[List[str], operator.add]  # Track which agents have been called


def create_initial_state(
    query: str,
    timestamp: Optional[float] = None,
    lecture_id: Optional[str] = None,
    conversation_history: Optional[List[BaseMessage]] = None
) -> AgentState:
    """
    Create an initial state for a new query.
    
    Args:
        query: User's question
        timestamp: Current video timestamp
        lecture_id: Identifier for the lecture
        conversation_history: Previous messages in the conversation
        
    Returns:
        Initial AgentState
    """
    return AgentState(
        messages=conversation_history or [],
        current_query=query,
        enriched_query=None,
        timestamp=timestamp,
        lecture_id=lecture_id,
        intent=None,
        target_namespaces=None,
        context=None,
        response=None,
        citations=None,
        metadata={},
        next_agent="metadata_agent",
        agent_history=[]
    )
