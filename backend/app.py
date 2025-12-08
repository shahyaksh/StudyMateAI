"""
Flask API for the LangGraph Multi-Agent System.

Provides REST endpoints for:
- Chat interactions with the agent system
- Quiz generation
- Flashcard generation
- Health checks
"""

import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_caching import Cache
from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage, AIMessage

from config import Config
from graph.workflow import run_agent_workflow

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'

# Enable CORS
CORS(app, supports_credentials=True)

# Initialize cache (for session management)
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 3600  # 1 hour
})

# In-memory session storage (replace with Redis in production)
conversation_sessions: Dict[str, Dict] = {}


def get_or_create_session(session_id: Optional[str] = None) -> str:
    """Get existing session or create a new one."""
    if session_id and session_id in conversation_sessions:
        return session_id
    
    # Create new session
    new_session_id = str(uuid.uuid4())
    conversation_sessions[new_session_id] = {
        'created_at': datetime.now().isoformat(),
        'messages': [],
        'lecture_id': None
    }
    return new_session_id


def get_conversation_history(session_id: str) -> List:
    """Get conversation history for a session."""
    if session_id not in conversation_sessions:
        return []
    return conversation_sessions[session_id]['messages']


def add_to_conversation_history(session_id: str, user_message: str, ai_response: str):
    """Add messages to conversation history."""
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'lecture_id': None
        }
    
    # Add messages
    conversation_sessions[session_id]['messages'].append(HumanMessage(content=user_message))
    conversation_sessions[session_id]['messages'].append(AIMessage(content=ai_response))
    
    # Keep only last N messages
    max_history = Config.MAX_CONVERSATION_HISTORY * 2  # *2 for user+ai pairs
    if len(conversation_sessions[session_id]['messages']) > max_history:
        conversation_sessions[session_id]['messages'] = \
            conversation_sessions[session_id]['messages'][-max_history:]


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(conversation_sessions)
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint.
    
    Request body:
    {
        "query": "What is attention mechanism?",
        "timestamp": 120.5,  // optional, video timestamp in seconds
        "lecture_id": "lecture_10",  // optional
        "session_id": "uuid"  // optional, for conversation continuity
    }
    
    Response:
    {
        "session_id": "uuid",
        "response": "Answer text...",
        "intent": "paper",
        "citations": [...],
        "metadata": {...}
    }
    """
    try:
        data = request.json
        
        # Validate request
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        query = data['query']
        timestamp = data.get('timestamp')
        lecture_id = data.get('lecture_id')
        session_id = data.get('session_id')
        
        # Get or create session (for session_id tracking only, no history)
        session_id = get_or_create_session(session_id)
        
        # Update lecture_id if provided
        if lecture_id:
            conversation_sessions[session_id]['lecture_id'] = lecture_id
        else:
            lecture_id = conversation_sessions[session_id].get('lecture_id')
        
        # Run agent workflow WITHOUT conversation history
        # Each query is treated independently for better performance
        final_state = run_agent_workflow(
            query=query,
            timestamp=timestamp,
            lecture_id=lecture_id,
            conversation_history=None  # No history - respond only to current query
        )
        
        # Extract response
        response_text = final_state.get('response', 'I apologize, but I could not generate a response.')
        intent = final_state.get('intent', 'unknown')
        citations = final_state.get('citations', [])
        metadata = final_state.get('metadata', {})
        
        # Format citations for response (handle None case for irrelevant queries)
        formatted_citations = []
        if citations:  # Only process if citations exist
            for citation in citations:
                if citation.get('type') == 'slide':
                    formatted_citations.append({
                        'source': f"Slide {citation.get('slide_number', 'N/A')}",
                        'text': citation.get('slide_title', '')
                    })
                elif citation.get('type') == 'transcript':
                    formatted_citations.append({
                        'source': 'Transcript',
                        'timestamp': f"{citation.get('start_time', 0)}-{citation.get('end_time', 0)}s",
                        'text': ''
                    })
        
        # NO LONGER STORING conversation in history - each query is independent
        # This improves model performance by avoiding context pollution
        
        response_data = {
            'session_id': session_id,
            'response': response_text,
            'intent': intent,
            'citations': formatted_citations,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        # If this is a quiz/flashcard intent, include the questions/cards in metadata
        if intent == 'quiz' and metadata.get('quiz_questions'):
            response_data['quiz_questions'] = metadata.get('quiz_questions')
        
        if intent == 'flashcard' and metadata.get('flashcards'):
            response_data['flashcards'] = metadata.get('flashcards')
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/quiz', methods=['POST'])
def generate_quiz():
    """
    Quiz generation endpoint.
    
    Request body:
    {
        "lecture_id": "lecture-7",
        "num_questions": 10
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        lecture_id = data.get('lecture_id')
        num_questions = data.get('num_questions', 10)
        
        if not lecture_id:
            return jsonify({'error': 'lecture_id is required'}), 400
        
        print(f"\n📝 Generating quiz for lecture: {lecture_id}, {num_questions} questions")
        
        # Run quiz generation workflow
        final_state = run_agent_workflow(
            query=f"Generate a quiz with {num_questions} questions",
            lecture_id=lecture_id,
            conversation_history=None
        )
        
        # Parse the response
        response_text = final_state.get('response', '{}')
        
        try:
            # Try to parse as JSON
            quiz_data = json.loads(response_text)
            questions = quiz_data.get('questions', [])
            
            return jsonify({
                'questions': questions
            })
        except json.JSONDecodeError:
            # If parsing fails, return error
            print(f"Failed to parse quiz response: {response_text[:200]}")
            return jsonify({
                'error': 'Failed to generate quiz',
                'questions': []
            }), 500
            
    except Exception as e:
        print(f"Error in quiz endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/flashcards', methods=['POST'])
def generate_flashcards():
    """
    Flashcard generation endpoint.
    
    Request body:
    {
        "topic": "attention mechanism",
        "num_cards": 10,  // optional, default 10
        "lecture_id": "lecture_10",  // optional
        "session_id": "uuid"  // optional
    }
    """
    try:
        data = request.json
        
        if not data or 'topic' not in data:
            return jsonify({'error': 'Missing topic parameter'}), 400
        
        topic = data['topic']
        num_cards = data.get('num_cards', 10)
        lecture_id = data.get('lecture_id')
        session_id = data.get('session_id')
        
        # Create flashcard query
        query = f"Generate {num_cards} flashcards about {topic}"
        
        # Get or create session
        session_id = get_or_create_session(session_id)
        
        # Run workflow
        final_state = run_agent_workflow(
            query=query,
            lecture_id=lecture_id,
            conversation_history=[]
        )
        
        response_text = final_state.get('response', '')
        metadata = final_state.get('metadata', {})
        
        return jsonify({
            'session_id': session_id,
            'flashcards_text': response_text,
            'flashcards': metadata.get('flashcards', []),
            'num_cards': metadata.get('num_cards', num_cards),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in flashcards endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id: str):
    """Get session information."""
    if session_id not in conversation_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session_data = conversation_sessions[session_id]
    
    return jsonify({
        'session_id': session_id,
        'created_at': session_data['created_at'],
        'lecture_id': session_data.get('lecture_id'),
        'message_count': len(session_data['messages']),
        'messages': [
            {
                'role': 'user' if isinstance(msg, HumanMessage) else 'assistant',
                'content': msg.content
            }
            for msg in session_data['messages']
        ]
    })


@app.route('/api/session/<session_id>', methods=['DELETE'])
def delete_session(session_id: str):
    """Delete a session."""
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]
        return jsonify({'message': 'Session deleted successfully'})
    return jsonify({'error': 'Session not found'}), 404


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting LangGraph Multi-Agent System API")
    print("="*60)
    print(f"Environment: {Config.FLASK_ENV}")
    print(f"Debug mode: {Config.FLASK_DEBUG}")
    print(f"LLM Model: {Config.LLM_MODEL}")
    print(f"Pinecone Papers Index: {Config.PINECONE_PAPERS_INDEX}")
    print("="*60 + "\n")
    
    # Validate configuration
    try:
        Config.validate()
        print("✅ Configuration validated successfully\n")
    except ValueError as e:
        print(f"❌ Configuration error: {e}\n")
        print("Please check your .env file and ensure all required variables are set.\n")
        exit(1)
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=Config.FLASK_DEBUG
    )
