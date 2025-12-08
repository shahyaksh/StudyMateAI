# Lecture RAG Backend

A sophisticated multi-agent system built with LangGraph for intelligent lecture content interaction. The system uses Retrieval Augmented Generation (RAG) to answer questions from lecture slides, transcripts, and research papers, while also generating quizzes and flashcards.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Development](#development)

## Features

- **Multi-Agent System**: Specialized agents for different content types and tasks
- **Intelligent Routing**: Supervisor agent classifies intent and routes queries
- **Context-Aware**: Maintains conversation history and enriches queries with temporal context
- **Multiple Knowledge Sources**: Retrieves from slides, transcripts, and research papers
- **Quiz Generation**: Creates multiple-choice quizzes from lecture content
- **Flashcard Creation**: Generates study flashcards automatically
- **Relevance Filtering**: Rejects queries unrelated to lecture content

## Architecture

The system uses a **LangGraph workflow** with conditional routing between specialized agents:

```
User Query → Supervisor Agent (Intent Classification)
                    ↓
        ┌───────────┼───────────┬──────────┬────────────┐
        ↓           ↓           ↓          ↓            ↓
   Irrelevant   Metadata    Paper     Quiz      Flashcard
    (Reject)     Agent      Agent     Agent       Agent
                    ↓
               Slides Agent
                    ↓
               Response
```

See [agents/README.md](agents/README.md) for detailed workflow documentation.

## Project Structure

```
backend/
├── app.py                      # Flask API server
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
│
├── agents/                     # Agent implementations
│   ├── state.py               # Shared agent state
│   ├── supervisor_agent.py    # Intent classification & routing
│   ├── metadata_agent.py      # Context enrichment
│   ├── slides_agent.py        # Slide content queries
│   ├── paper_agent.py         # Research paper queries
│   ├── quiz_agent.py          # Quiz generation
│   └── flashcard_agent.py     # Flashcard generation
│
├── graph/                      # LangGraph workflow
│   └── workflow.py            # Agent graph definition
│
├── services/                   # External services
│   └── pinecone_service.py    # Vector database integration
│
├── utils/                      # Utilities
│   ├── prompts.py             # Prompt templates
│   ├── prompt_loader.py       # YAML prompt loader
│   └── transcript_loader.py   # Transcript context retrieval
│
├── config/                     # Configuration files
│   └── prompts.yaml           # Agent prompts
│
├── scripts/                    # Utility scripts
│   ├── setup/                 # Setup scripts
│   ├── indexing/              # Data indexing
│   └── preprocessing/         # Data preprocessing
│
├── data/                       # Data storage
│   ├── raw_data/              # Raw lecture materials
│   ├── processed_data/        # Processed outputs
│   └── examples/              # Example data
│
├── evaluation/                 # RAGAS evaluation framework
│   └── README.md              # Evaluation documentation
│
└── notebooks/                  # Jupyter notebooks
```

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key
- Pinecone account and API key
- Pinecone index with namespaces: `slides`, `papers`, `transcript`

### Installation

1. **Clone and navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

   Required variables:
   ```ini
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=lecture-rag-index
   PINECONE_ENVIRONMENT=us-east-1
   LLM_MODEL=gpt-4o-mini
   EMBEDDING_MODEL=text-embedding-3-large
   SECRET_KEY=your-secret-key
   ```

5. **Set up Pinecone index** (if not already created):
   ```bash
   python -m scripts.setup.setup_pinecone
   ```

6. **Index your data** (if not already indexed):
   ```bash
   python -m scripts.indexing.index_all
   ```

### Running the Server

```bash
python app.py
```

Server will start on `http://localhost:5000`

## API Endpoints

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-08T12:00:00"
}
```

### Chat

Send queries to the multi-agent system.

```http
POST /api/chat
Content-Type: application/json

{
  "query": "What is instruction tuning?",
  "timestamp": 120.5,           // Optional: video timestamp in seconds
  "lecture_id": "lecture-7",    // Optional: lecture identifier
  "session_id": "uuid"          // Optional: for conversation continuity
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Instruction tuning is a technique...",
  "intent": "general",
  "citations": [
    {
      "slide_number": 15,
      "slide_title": "Instruction Tuning",
      "content": "..."
    }
  ],
  "metadata": {
    "agents_called": ["supervisor_agent", "metadata_agent", "slides_agent"],
    "num_contexts": 3
  }
}
```

**Intent Types:**
- `general` - Slide/transcript queries
- `paper` - Research paper queries
- `quiz` - Quiz generation request
- `flashcard` - Flashcard generation request
- `irrelevant` - Query rejected (not lecture-related)

### Generate Quiz

Create a multiple-choice quiz from lecture content.

```http
POST /api/quiz
Content-Type: application/json

{
  "lecture_id": "lecture-7",
  "num_questions": 5
}
```

**Response:**
```json
{
  "quiz_questions": [
    {
      "question": "What is the main purpose of instruction tuning?",
      "options": {
        "A": "To reduce model size",
        "B": "To improve model performance on specific tasks",
        "C": "To increase training speed",
        "D": "To reduce computational cost"
      },
      "correct_answer": "B",
      "explanation": "Instruction tuning fine-tunes models...",
      "difficulty": "medium",
      "topic": "Instruction Tuning"
    }
  ]
}
```

### Generate Flashcards

Create study flashcards from lecture content.

```http
POST /api/flashcards
Content-Type: application/json

{
  "lecture_id": "lecture-7",
  "num_cards": 10
}
```

**Response:**
```json
{
  "flashcards": [
    {
      "front": "What is instruction tuning?",
      "back": "A technique to fine-tune language models..."
    }
  ]
}
```

### Session Management

```http
GET /api/session/<session_id>
```

Get conversation history for a session.

```http
DELETE /api/session/<session_id>
```

Clear conversation history for a session.

## Configuration

### LLM Model

Edit `config.py` or set environment variable:

```python
LLM_MODEL = "gpt-4o-mini"  # or "gpt-4o", "gpt-4-turbo"
```

### Embedding Model

```python
EMBEDDING_MODEL = "text-embedding-3-large"  # or "text-embedding-3-small"
```

### Prompts

Agent prompts are defined in `config/prompts.yaml`. Edit this file to customize agent behavior.

### Pinecone Configuration

```python
PINECONE_INDEX_NAME = "lecture-rag-index"
PINECONE_ENVIRONMENT = "us-east-1"
```

## Development

### Running Tests

```bash
# Run agent tests
python test_agents.py

# Run evaluation
cd evaluation
python agent_evaluation_runner.py
python ragas_eval_wrapper.py
```

### Adding New Agents

1. Create agent file in `agents/` directory
2. Implement agent node function
3. Add agent to `graph/workflow.py`
4. Update routing logic in `route_after_supervisor()`
5. Add prompts to `config/prompts.yaml`

### Logging

The system uses professional logging format:

```
[WORKFLOW] Starting Agent Workflow
[SUPERVISOR] Detecting intent and routing...
[METADATA] Checking if query is about current professor teaching...
[SLIDES] Retrieving slide information...
[WORKFLOW] Workflow Complete
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build backend only
docker build -t lecture-rag-backend .
docker run -p 5000:5000 --env-file .env lecture-rag-backend
```

See [DOCKER_GUIDE.md](../DOCKER_GUIDE.md) for detailed Docker documentation.

## Troubleshooting

### "OPENAI_API_KEY not found"
- Ensure `.env` file exists in backend directory
- Verify API key is valid

### "Pinecone index not found"
- Run `python -m scripts.setup.setup_pinecone`
- Verify index name in `.env` matches Pinecone dashboard

### "No contexts retrieved"
- Ensure data is indexed: `python -m scripts.indexing.index_all`
- Check Pinecone index has vectors in correct namespaces

### Agent not responding
- Check Flask server logs for errors
- Verify OpenAI API key has sufficient credits
- Ensure Pinecone API key is valid

## Performance

- **Average response time**: 2-4 seconds
- **Quiz generation**: 10-15 seconds for 5 questions
- **Flashcard generation**: 8-12 seconds for 10 cards
- **Concurrent requests**: Supports multiple simultaneous users

## Security

- API keys stored in `.env` (never committed)
- Session data stored in-memory (use Redis for production)
- Input validation on all endpoints
- CORS enabled for frontend integration

## License

MIT License

## Support

For issues or questions:
1. Check [agents/README.md](agents/README.md) for workflow details
2. Review [evaluation/README.md](evaluation/README.md) for evaluation
3. See [scripts/README.md](scripts/README.md) for utility scripts
