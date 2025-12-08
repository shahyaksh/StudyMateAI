"""Prompt templates for all agents in the system.

All prompts are now loaded from config/prompts.yaml for easier management.
"""

from utils.prompt_loader import get_prompt

# Load prompts from YAML
SUPERVISOR_AGENT_SYSTEM_PROMPT = get_prompt('supervisor', 'system_prompt')
PAPER_AGENT_SYSTEM_PROMPT = get_prompt('paper', 'system_prompt')
SLIDES_AGENT_SYSTEM_PROMPT = get_prompt('slides', 'system_prompt')
QUIZ_GENERATOR_SYSTEM_PROMPT = get_prompt('quiz', 'system_prompt')
FLASHCARD_GENERATOR_SYSTEM_PROMPT = get_prompt('flashcard', 'system_prompt')

# Metadata agent prompts
METADATA_CURRENT_TEACHING_CHECK = get_prompt('metadata', 'current_teaching_check')
METADATA_ENRICHMENT_PROMPT = get_prompt('metadata', 'enrichment_prompt')


def format_conversation_history(messages: list) -> str:
    """Format conversation history for prompts."""
    if not messages:
        return "No previous conversation."
    
    formatted = []
    for msg in messages[-10:]:  # Last 10 messages
        role = msg.__class__.__name__.replace("Message", "")
        formatted.append(f"{role}: {msg.content}")
    
    return "\n".join(formatted)


def format_context(context_docs: list) -> str:
    """Format retrieved documents for prompts."""
    if not context_docs:
        return "No relevant context found."
    
    formatted = []
    for i, doc in enumerate(context_docs, 1):
        metadata = doc.get("metadata", {})
        content = doc.get("content", "")
        
        # Format based on namespace
        namespace = metadata.get("namespace", "unknown")
        
        if namespace == "papers":
            formatted.append(
                f"[Paper {i}] {metadata.get('title', 'Unknown')} "
                f"(Page {metadata.get('page', 'N/A')})\n{content}"
            )
        elif namespace == "slides":
            formatted.append(
                f"[Slide {metadata.get('slide_number', 'N/A')}] "
                f"{metadata.get('slide_title', '')}\n{content}"
            )
        elif namespace == "transcript":
            formatted.append(
                f"[Transcript {metadata.get('start_time', 'N/A')}s - "
                f"{metadata.get('end_time', 'N/A')}s]\n{content}"
            )
        else:
            formatted.append(f"[Document {i}]\n{content}")
    
    return "\n\n---\n\n".join(formatted)
