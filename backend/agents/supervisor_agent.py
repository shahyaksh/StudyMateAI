"""
Supervisor Agent - Detects intent and routes to appropriate specialized agent.

This agent:
1. Analyzes the enriched query
2. Classifies the intent (paper/slide/quiz/flashcard/general)
3. Determines which Pinecone namespaces to search
4. Routes to the appropriate specialized agent
"""

from typing import Dict
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from utils.prompts import SUPERVISOR_AGENT_SYSTEM_PROMPT
from config import Config


def supervisor_agent_node(state: AgentState) -> Dict:
    """
    Supervisor agent node for LangGraph workflow.
    
    Detects intent and determines routing.
    Rejects irrelevant queries that are not about the lecture content.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with intent and routing information
    """
    print("[SUPERVISOR] Detecting intent and routing...")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=Config.LLM_MODEL,
        temperature=0.3,
        openai_api_key=Config.OPENAI_API_KEY
    )
    
    # Use enriched query if available, otherwise use original
    query = state.get("enriched_query") or state["current_query"]
    
    # Create prompt with irrelevant query detection
    prompt = SUPERVISOR_AGENT_SYSTEM_PROMPT.format(
        query=query,
        timestamp=state.get("timestamp", "N/A"),
        lecture_id=state.get("lecture_id", "N/A")
    )
    
    # Get routing decision from LLM
    messages = [SystemMessage(content=prompt)]
    response = llm.invoke(messages)
    
    # Parse JSON response
    try:
        decision = json.loads(response.content.strip())
        intent = decision.get("intent", "general")
        namespaces = decision.get("namespaces", ["transcript", "slides"])
        reasoning = decision.get("reasoning", "")
        is_relevant = decision.get("is_relevant", True)  # New field
        
        print(f"   Intent: {intent}")
        print(f"   Relevant: {is_relevant}")
        print(f"   Namespaces: {namespaces}")
        print(f"   Reasoning: {reasoning}")
        
        # Check if query is irrelevant
        if not is_relevant or intent == "irrelevant":
            print("[SUPERVISOR] Query is irrelevant to lecture content - rejecting")
            return {
                "intent": "irrelevant",
                "response": "I can't help with that. I'm designed to answer questions about lecture content, slides, and research papers related to this course. Please ask a question about the lecture material.",
                "agent_history": ["supervisor_agent"],
                "next_agent": None  # End workflow
            }
        
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        print("   Warning: Failed to parse supervisor response, using defaults")
        intent = "general"
        namespaces = ["transcript", "slides"]
    
    # Determine next agent based on intent
    next_agent_map = {
        "paper": "paper_agent",
        "slide": "slides_agent",
        "quiz": "quiz_agent",
        "flashcard": "flashcard_agent",
        "general": "slides_agent"  # Default to slides for general queries
    }
    
    next_agent = next_agent_map.get(intent, "slides_agent")
    
    # Update state
    return {
        "intent": intent,
        "target_namespaces": namespaces,
        "agent_history": ["supervisor_agent"],
        "next_agent": next_agent
    }
