"""
LangGraph workflow definition for the multi-agent system.

This module creates the agent graph with nodes for each agent and
conditional edges for routing between agents.
"""

from typing import Dict, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from agents.state import AgentState
from agents.metadata_agent import metadata_agent_node
from agents.supervisor_agent import supervisor_agent_node
from agents.paper_agent import paper_agent_node
from agents.slides_agent import slides_agent_node
from agents.quiz_agent import quiz_agent_node
from agents.flashcard_agent import flashcard_agent_node


def route_after_supervisor(state: AgentState) -> Literal["metadata_agent", "paper_agent", "quiz_agent", "flashcard_agent", "__end__"]:
    """
    Routing function to determine which agent to call after supervisor.
    
    NEW LOGIC:
    - If intent is "irrelevant" -> END (reject query)
    - If intent is "slide" or "general" -> metadata_agent (needs transcript context)
    - If intent is "paper" -> paper_agent directly (no transcript needed)
    - If intent is "quiz" or "flashcard" -> respective agent directly
    
    Args:
        state: Current agent state
        
    Returns:
        Name of the next agent to call or END
    """
    intent = state.get("intent", "general")
    
    if intent == "irrelevant":
        return "__end__"
    
    if intent == "paper":
        return "paper_agent"
    elif intent == "quiz":
        return "quiz_agent"
    elif intent == "flashcard":
        return "flashcard_agent"
    else:
        return "metadata_agent"


def route_after_metadata(state: AgentState) -> Literal["slides_agent"]:
    """
    After metadata agent enriches the query with transcript context,
    always route to slides agent.
    """
    return "slides_agent"


def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow for the multi-agent system.
    
    NEW WORKFLOW:
    START -> Supervisor (determines intent)
          -> If paper/quiz/flashcard: go directly to that agent
          -> If slide/general: go to Metadata Agent -> Slides Agent
    
    Returns:
        Compiled StateGraph
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor_agent", supervisor_agent_node)
    workflow.add_node("metadata_agent", metadata_agent_node)
    workflow.add_node("paper_agent", paper_agent_node)
    workflow.add_node("slides_agent", slides_agent_node)
    workflow.add_node("quiz_agent", quiz_agent_node)
    workflow.add_node("flashcard_agent", flashcard_agent_node)
    
    workflow.set_entry_point("supervisor_agent")
    
    workflow.add_conditional_edges(
        "supervisor_agent",
        route_after_supervisor,
        {
            "__end__": END,
            "metadata_agent": "metadata_agent",
            "paper_agent": "paper_agent",
            "quiz_agent": "quiz_agent",
            "flashcard_agent": "flashcard_agent",
        }
    )
    
    workflow.add_edge("metadata_agent", "slides_agent")
    
    workflow.add_edge("paper_agent", END)
    workflow.add_edge("slides_agent", END)
    workflow.add_edge("quiz_agent", END)
    workflow.add_edge("flashcard_agent", END)
    
    return workflow.compile()


def run_agent_workflow(
    query: str,
    timestamp: float = None,
    lecture_id: str = None,
    conversation_history: list = None
) -> Dict:
    """
    Run the agent workflow for a user query.
    
    Args:
        query: User's question
        timestamp: Current video timestamp in seconds
        lecture_id: Identifier for the lecture
        conversation_history: Previous messages in the conversation
        
    Returns:
        Final state with response
    """
    from agents.state import create_initial_state
    
    print("\n" + "="*60)
    print("[WORKFLOW] Starting Agent Workflow")
    print("="*60)
    print(f"[WORKFLOW] Query: {query}")
    print(f"[WORKFLOW] Timestamp: {timestamp}")
    print(f"[WORKFLOW] Lecture ID: {lecture_id}")
    print("="*60 + "\n")
    
    initial_state = create_initial_state(
        query=query,
        timestamp=timestamp,
        lecture_id=lecture_id,
        conversation_history=conversation_history
    )
    
    graph = create_agent_graph()
    
    final_state = graph.invoke(initial_state)
    
    print("\n" + "="*60)
    print("[WORKFLOW] Workflow Complete")
    print("="*60)
    print(f"[WORKFLOW] Intent: {final_state.get('intent')}")
    print(f"[WORKFLOW] Agents called: {final_state.get('agent_history')}")
    print(f"[WORKFLOW] Response length: {len(final_state.get('response', ''))} characters")
    print("="*60 + "\n")
    
    return final_state


# For visualization (optional)
def visualize_graph():
    """
    Visualize the agent graph structure.
    Requires graphviz to be installed.
    """
    try:
        from IPython.display import Image, display
        graph = create_agent_graph()
        display(Image(graph.get_graph().draw_mermaid_png()))
    except ImportError:
        print("Install graphviz and IPython to visualize the graph")
        print("The graph structure is:")
        print("  START -> supervisor_agent")
        print("    -> If paper/quiz/flashcard: go directly to that agent")
        print("    -> If slide/general: metadata_agent -> slides_agent")
        print("  All agents -> END")
