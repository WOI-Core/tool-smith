# uvicorn app.main:app --reload
# app/main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from io import BytesIO
import zipfile

from core.services.graph_manager import GraphManager, get_graph_manager
from core.models.pydantic_models import TaskRequest

app = FastAPI(title="Toolsmith API")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Toolsmith API is running!"}

@app.post("/generate-preview")
async def generate_preview_endpoint(
    req: TaskRequest,
    graph_manager: GraphManager = Depends(get_graph_manager)
):
    final_state = await graph_manager.execute_graph(req)

    if not final_state.get("files") or final_state.get("error"):
        raise HTTPException(status_code=500, detail=final_state.get("error", "Unknown error"))

    task_name = final_state.get("task_name", "task")
    files = final_state.get("files", [])
    
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zipf:
        # ใน ZIP จะมีโฟลเดอร์หลักครอบอยู่
        for file_info in files:
            zipf.writestr(f"{task_name}/{file_info['file_path']}", file_info['content'])
    buffer.seek(0)

    zip_filename = f"{task_name}_tasks.zip"
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
    )