from fastapi import UploadFile
import os
import zipfile
import json
from tempfile import TemporaryDirectory
import subprocess

REPO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "woi-grader-archive/ToolSmith")

async def gitUpload(file: UploadFile):
    with TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, file.filename)

        # Save uploaded zip file
        with open(zip_path, "wb") as f:
            f.write(await file.read())

        # Preview zip file content to extract config.json first
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # หา config.json
            config_filename = None
            for name in zip_ref.namelist():
                if name.endswith("config.json"):
                    config_filename = name
                    break
            
            if config_filename is None:
                raise ValueError("config.json not found in zip file")

            # อ่าน config.json และโหลด title
            with zip_ref.open(config_filename) as config_file:
                config = json.load(config_file)
                folder_name = config.get("title", "untitled").strip().replace(" ", "_")

            # สร้างโฟลเดอร์ตาม title
            dest_folder = os.path.join(REPO_PATH, folder_name)
            os.makedirs(dest_folder, exist_ok=True)

            # แตกไฟล์ทั้งหมดลงในโฟลเดอร์
            zip_ref.extractall(dest_folder)

        # git add, commit, push
        subprocess.run(["git", "add", "."], cwd=REPO_PATH, check=True)
        subprocess.run(["git", "commit", "-m", f"Upload from web UI: {file.filename} (as {folder_name})"], cwd=REPO_PATH, check=True)
        subprocess.run(["git", "push"], cwd=REPO_PATH, check=True)
