"""
Metadata Agent - Maintains conversation context and enriches user queries.

This agent:
1. Analyzes conversation history
2. Resolves references (this, that, previous, etc.)
3. Adds temporal context from video timestamp AND transcript text
4. Rewrites queries to be more specific and searchable
"""

from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from agents.state import AgentState
from utils.prompts import METADATA_CURRENT_TEACHING_CHECK, METADATA_ENRICHMENT_PROMPT
from utils.transcript_loader import get_transcript_context
from config import Config


def metadata_agent_node(state: AgentState) -> Dict:
    """
    Metadata agent node for LangGraph workflow.
    
    ONLY enriches queries when student asks about what professor is currently teaching.
    Examples: "what is the professor talking about?", "what is being discussed?", "what's the current topic?"
    
    For all other queries (specific questions, concepts, etc.), returns original query unchanged.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with enriched query (or original if not about current teaching)
    """
    print("[METADATA] Checking if query is about current professor teaching...")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=Config.LLM_MODEL,
        temperature=0.3,
        openai_api_key=Config.OPENAI_API_KEY
    )
    
    # Get transcript context if timestamp and lecture_id are provided
    transcript_context = ""
    if state.get('timestamp') is not None and state.get('lecture_id'):
        transcript_context = get_transcript_context(
            lecture_id=state['lecture_id'],
            timestamp=state['timestamp'],
            num_segments=3  # Previous 2 + current segment
        )
        print(f"   Loaded transcript context ({len(transcript_context)} chars)")
    
    # If no transcript context, return original query
    if not transcript_context:
        print("   No transcript context available - using original query")
        return {
            "enriched_query": state['current_query'],
            "agent_history": ["metadata_agent"],
            "next_agent": "supervisor_agent"
        }
    
    # Check if query is asking about what professor is currently teaching/discussing
    intent_check_prompt = METADATA_CURRENT_TEACHING_CHECK.format(query=state['current_query'])

    intent_response = llm.invoke([HumanMessage(content=intent_check_prompt)])
    is_about_current_teaching = intent_response.content.strip().upper() == "YES"
    
    if not is_about_current_teaching:
        print("   Query is NOT about current teaching - using original query")
        return {
            "enriched_query": state['current_query'],
            "agent_history": ["metadata_agent"],
            "next_agent": "supervisor_agent"
        }
    
    print("   Query IS about current teaching - enriching with transcript context")
    
    # Enrich query with what professor is actually teaching
    enrichment_prompt = METADATA_ENRICHMENT_PROMPT.format(transcript_context=transcript_context)

    enrichment_response = llm.invoke([HumanMessage(content=enrichment_prompt)])
    enriched_query = enrichment_response.content.strip()
    
    print(f"   Original query: {state['current_query']}")
    print(f"   Enriched query: {enriched_query}")
    
    # Update state
    return {
        "enriched_query": enriched_query,
        "agent_history": ["metadata_agent"],
        "next_agent": "supervisor_agent"
    }
