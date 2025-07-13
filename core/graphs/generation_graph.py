# core/graphs/generation_graph.py
from langgraph.graph import StateGraph, END
from core.models.graph_models import GraphState  # <--- แก้ไขตรงนี้
from .nodes.generation import generate_content_node
from .nodes.file_creation import create_files_node

def create_workflow():
    """Creates and compiles the LangGraph workflow."""
    workflow = StateGraph(GraphState)
    workflow.add_node("generator", generate_content_node)
    workflow.add_node("file_creator", create_files_node)

    workflow.set_entry_point("generator")
    workflow.add_edge("generator", "file_creator")
    workflow.add_edge("file_creator", END)
    
    return workflow.compile()