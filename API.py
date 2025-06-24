# fastapi dev API.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from toolSmith import generate_task
from gitUpload import gitUpload
from io import BytesIO
import zipfile

app = FastAPI()

class contentName(BaseModel):
    content_name: str
    cases_size: int
    detail: str

@app.post("/tool-smith")
async def task_gen(req: contentName):
    task_files = await generate_task(req)

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zipf:
        for upload_file in task_files:
            upload_file.file.seek(0)
            zipf.writestr(upload_file.filename, upload_file.file.read())
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/zip", headers={
        "Content-Disposition": f"attachment; filename={req.content_name}_tasks.zip"
    })

@app.post("/grader-upload")
async def task_gen(file: UploadFile = File(...)):
    await gitUpload(file)
    return "success"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)