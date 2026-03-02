# core/services/graph_manager.py
from core.graphs.generation_graph import create_workflow
from core.models.pydantic_models import TaskRequest

class GraphManager:
    def __init__(self):
        self.workflow = create_workflow()

    async def execute_graph(self, request: TaskRequest) -> dict:
        """Executes the graph with the initial state."""
        initial_state = {"request": request, "error": None}
        return await self.workflow.ainvoke(initial_state)

# Dependency Injection
def get_graph_manager():
    yield GraphManager()