"""
Flashcard Generator Agent - Generates flashcards from lecture content.

This agent:
1. Retrieves relevant lecture content
2. Extracts key concepts and definitions
3. Creates question-answer pairs
4. Supports different flashcard types
"""

from typing import Dict
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from services.pinecone_service import get_pinecone_service
from utils.prompts import FLASHCARD_GENERATOR_SYSTEM_PROMPT, format_context
from utils.langfuse_tracking import track_agent
from config import Config


@track_agent("flashcard_agent")
def flashcard_agent_node(state: AgentState) -> Dict:
    """
    Flashcard generator agent node for LangGraph workflow.
    
    Generates flashcards from ALL lecture slides for comprehensive coverage.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with flashcards
    """
    print("🗂️  Flashcard Agent: Generating flashcards from all slide content...")
    
    # Get Pinecone service
    pinecone_service = get_pinecone_service()
    
    # Get lecture_id to retrieve all slides for that lecture
    lecture_id = state.get("lecture_id", "")
    
    # Retrieve ALL slides for comprehensive coverage
    all_slides = pinecone_service.query_namespace(
        query="lecture content topics concepts",  # Broad query to get all slides
        namespace=Config.NAMESPACE_SLIDES,
        top_k=50  # Get many slides to cover all topics
    )
    
    print(f"   Retrieved {len(all_slides)} slides for comprehensive flashcard generation")
    
    # Format slide content
    formatted_content = format_context(all_slides)
    
    # Get number of flashcards (default 10)
    num_cards = state.get("num_cards", 10)
    
    # Get Langfuse callback handler for token tracking
    from utils.langfuse_tracking import get_langfuse_callback_handler
    callback_handler = get_langfuse_callback_handler(
        trace_name="flashcard_agent",
        session_id=state.get("session_id"),
        metadata={"num_cards": num_cards, "num_slides": len(all_slides)}
    )
    
    # Initialize LLM with callback for token tracking
    llm = ChatOpenAI(
        model=Config.LLM_MODEL,
        temperature=0.7,  # Slightly higher for creative question generation
        openai_api_key=Config.OPENAI_API_KEY,
        max_tokens=4000,  # More tokens for multiple flashcards
        callbacks=[callback_handler]
    )
    
    # Create prompt
    prompt = FLASHCARD_GENERATOR_SYSTEM_PROMPT.format(
        content=formatted_content,
        num_cards=num_cards
    )
    
    # Generate flashcards
    messages = [SystemMessage(content=prompt)]
    response = llm.invoke(messages)
    
    print(f"   Raw LLM response length: {len(response.content)} chars")
    
    # Parse JSON response
    try:
        # Clean the response - remove markdown code blocks if present
        content = response.content.strip()
        if content.startswith('```json'):
            content = content[7:]  # Remove ```json
        if content.startswith('```'):
            content = content[3:]  # Remove ```
        if content.endswith('```'):
            content = content[:-3]  # Remove trailing ```
        content = content.strip()
        
        flashcard_data = json.loads(content)
        flashcards = flashcard_data.get("flashcards", [])
        
        if not flashcards:
            print("   Warning: No flashcards generated")
            return {
                "response": "Failed to generate flashcards. Please try again.",
                "metadata": {"flashcards": [], "num_cards": 0},
                "agent_history": ["flashcard_agent"],
                "next_agent": None
            }
        
        print(f"   Generated {len(flashcards)} flashcards")
        
        # Create user-friendly response message
        types = set(card.get('type', 'concept') for card in flashcards)
        types_str = ', '.join(sorted(types)[:3])  # Show first 3 types
        
        friendly_message = f"I've created {len(flashcards)} flashcards covering {types_str} and more. Click the button below to start studying!"
        
        # Update state with friendly message and flashcards in metadata
        return {
            "response": friendly_message,
            "metadata": {
                "flashcards": flashcards,
                "num_cards": len(flashcards)
            },
            "agent_history": ["flashcard_agent"],
            "next_agent": None
        }
        
    except json.JSONDecodeError as e:
        print(f"   Error parsing flashcard JSON: {e}")
        print(f"   Response content: {response.content[:500]}")
        return {
            "response": "Failed to generate flashcards. Please try again.",
            "metadata": {"flashcards": [], "num_cards": 0},
            "agent_history": ["flashcard_agent"],
            "next_agent": None
        }
