"""
Quiz Generator Agent - Generates quizzes from lecture content.

This agent:
1. Retrieves relevant lecture content (slides, transcripts)
2. Generates multiple-choice questions
3. Provides answer key with explanations
4. Supports different difficulty levels
"""

from typing import Dict
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from agents.state import AgentState
from services.pinecone_service import get_pinecone_service
from utils.prompts import QUIZ_GENERATOR_SYSTEM_PROMPT, format_context
from utils.langfuse_tracking import track_agent
from config import Config


@track_agent("quiz_agent")
def quiz_agent_node(state: AgentState) -> Dict:
    """
    Quiz agent node for LangGraph workflow.
    
    Generates quiz questions based on ALL slide content to ensure comprehensive coverage.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with quiz questions
    """
    print("📝 Quiz Agent: Generating quiz questions from all slide content...")
    
    # Get Pinecone service
    pinecone_service = get_pinecone_service()
    
    # Get lecture_id to retrieve all slides for that lecture
    lecture_id = state.get("lecture_id", "")
    
    # Retrieve ALL slides for comprehensive topic coverage
    # Use a broad query to get all content
    all_slides = pinecone_service.query_namespace(
        query="lecture content topics concepts",  # Broad query to get all slides
        namespace=Config.NAMESPACE_SLIDES,
        top_k=50  # Get many slides to cover all topics
    )
    
    print(f"   Retrieved {len(all_slides)} slides for comprehensive quiz generation")
    
    # Format slide content
    formatted_content = format_context(all_slides)
    
    # Get number of questions (default 10)
    num_questions = state.get("num_questions", 10)
    
    # Get Langfuse callback handler for token tracking
    from utils.langfuse_tracking import get_langfuse_callback_handler
    callback_handler = get_langfuse_callback_handler(
        trace_name="quiz_agent",
        session_id=state.get("session_id"),
        metadata={"num_questions": num_questions, "num_slides": len(all_slides)}
    )
    
    # Initialize LLM with callback for token tracking
    llm = ChatOpenAI(
        model=Config.LLM_MODEL,
        temperature=0.7,  # Slightly higher for creative question generation
        openai_api_key=Config.OPENAI_API_KEY,
        max_tokens=4000,  # More tokens for multiple questions
        callbacks=[callback_handler]
    )
    
    # Create prompt
    prompt = QUIZ_GENERATOR_SYSTEM_PROMPT.format(
        num_questions=num_questions,
        content=formatted_content
    )
    
    # Generate quiz
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
        
        quiz_data = json.loads(content)
        questions = quiz_data.get("questions", [])
        
        if not questions:
            print("   Warning: No questions generated")
            return {
                "response": json.dumps({"questions": []}, indent=2),
                "quiz_questions": [],
                "agent_history": ["quiz_agent"],
                "next_agent": None
            }
        
        print(f"   Generated {len(questions)} exam-appropriate questions")
        
        # Create user-friendly response message
        topics = set(q.get('topic', 'General') for q in questions)
        topics_str = ', '.join(sorted(topics)[:3])  # Show first 3 topics
        
        friendly_message = f"I've generated a {num_questions}-question quiz covering topics like {topics_str}. Click the button below to start!"
        
        # Update state with friendly message and questions in metadata
        return {
            "response": friendly_message,
            "metadata": {
                "quiz_questions": questions,
                "num_questions": len(questions)
            },
            "agent_history": ["quiz_agent"],
            "next_agent": None
        }
    except json.JSONDecodeError as e:
        print(f"   Error parsing quiz JSON: {e}")
        print(f"   Response content: {response.content[:500]}")
        return {
            "response": json.dumps({"questions": []}, indent=2),
            "quiz_questions": [],
            "agent_history": ["quiz_agent"],
            "next_agent": None
        }
