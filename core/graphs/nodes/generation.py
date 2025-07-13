# core/graphs/nodes/generation.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from core.services.config import settings
from core.models.graph_models import GraphState  # <--- แก้ไขตรงนี้
from pathlib import Path

# Load prompt from file
prompt_path = Path(__file__).parents[2] / "prompts/task_generation_prompt.txt"
prompt_template = PromptTemplate.from_template(prompt_path.read_text(encoding="utf-8"))

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=settings.google_api_key)
chain = prompt_template | llm

async def generate_content_node(state: GraphState) -> dict:
    """Generates task content using the LLM based on the request."""
    print("--- NODE: GENERATING CONTENT ---")
    req = state["request"]
    # ... (ส่วนที่เหลือของฟังก์ชันเหมือนเดิม) ...
    try:
        response = await chain.ainvoke({
            "content": req.content_name,
            "casesSize": req.cases_size,
            "detail": req.detail
        })
        return {"llm_output": response.content}
    except Exception as e:
        return {"error": f"LLM generation failed: {e}"}
