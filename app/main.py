# fastapi dev toolsmith/app/main.py
# app/main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from io import BytesIO
import zipfile

from core.services.graph_manager import GraphManager, get_graph_manager
# --- แก้ไขการ import ---
from core.services.storage_service import StorageService, get_storage_service
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

@app.post("/upload-task")
async def upload_task_endpoint(
    content_name: str = Form(...),
    cases_size: int = Form(...),
    detail: str = Form(...),
    file: UploadFile = File(...),
    graph_manager: GraphManager = Depends(get_graph_manager),
    storage_service: StorageService = Depends(get_storage_service)
):
    """
    Accepts a zip file and metadata, processes it, and uploads the files to Supabase Storage.
    """
    try:
        # --- แปลงข้อมูลให้อยู่ในรูปแบบที่ GraphManager ใช้ได้ ---
        req = TaskRequest(
            content_name=content_name,
            cases_size=cases_size,
            detail=detail
        )

        print("Running graph to generate files for bucket upload...")
        final_state = await graph_manager.execute_graph(req)

        if not final_state.get("files") or final_state.get("task_name") is None:
            raise HTTPException(status_code=500, detail=final_state.get("error", "An internal error occurred during generation."))

        task_name = final_state["task_name"]
        files = final_state["files"]

        # --- อัปโหลดไฟล์จาก final_state (ไฟล์ที่ generate แล้ว) ---
        storage_service.upload_files(task_name, files)

        return JSONResponse(status_code=200, content={"message": f"Task '{task_name}' and its {len(files)} files uploaded to bucket successfully!"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload to bucket failed: {str(e)}")