"""
Langfuse tracking module for agent latency analysis.

This module provides decorators and utilities to track agent execution
with Langfuse for latency monitoring and performance analysis.
"""

from langfuse import observe, Langfuse
from langfuse.langchain import CallbackHandler
import os
from typing import Any, Dict, Optional
from functools import wraps
import inspect

# Initialize Langfuse client
langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

def track_agent(agent_name: str):
    """
    Decorator to track agent execution with query, response, and token usage.
    
    This decorator automatically captures:
    - Agent execution time (latency)
    - Input/output data
    - Token usage (if available)
    - Errors and exceptions
    
    Args:
        agent_name: Name of the agent (e.g., 'supervisor_agent', 'slides_agent')
    
    Example:
        @track_agent("supervisor_agent")
        def supervisor_agent_node(state: AgentState) -> Dict:
            # Agent logic here
            return updated_state
    """
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @observe(name=agent_name)
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Execute the agent function
                result = await func(*args, **kwargs)
                return result
            return async_wrapper
        else:
            @observe(name=agent_name)
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Execute the agent function
                result = func(*args, **kwargs)
                return result
            return sync_wrapper
    return decorator

def get_langfuse_callback_handler(
    trace_name: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> CallbackHandler:
    """
    Get a LangChain callback handler for Langfuse.
    
    This enables automatic token usage and cost tracking for LangChain LLM calls.
    
    Note: The CallbackHandler uses environment variables for configuration:
    - LANGFUSE_SECRET_KEY
    - LANGFUSE_PUBLIC_KEY
    - LANGFUSE_HOST
    
    Args:
        trace_name: Name for the trace (ignored, kept for API compatibility)
        session_id: Session identifier (ignored, kept for API compatibility)
        user_id: User identifier (ignored, kept for API compatibility)
        metadata: Additional metadata (ignored, kept for API compatibility)
    
    Returns:
        CallbackHandler instance to pass to LangChain LLM calls
    
    Example:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            callbacks=[get_langfuse_callback_handler()]
        )
        response = llm.invoke(messages)
    """
    return CallbackHandler()


def flush_langfuse():
    """
    Flush all pending Langfuse events.
    
    Call this at the end of your application or after processing
    a batch of requests to ensure all events are sent to Langfuse.
    """
    langfuse.flush()

def get_langfuse_client():
    """
    Get the Langfuse client instance.
    
    Returns:
        Langfuse client instance
    """
    return langfuse
