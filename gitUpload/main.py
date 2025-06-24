# git_upload.py

from fastapi import UploadFile
import os
import zipfile
import json
from tempfile import TemporaryDirectory
import subprocess
from MD_PDF import MD_PDF  # <-- import จากไฟล์ที่แยกไว้

REPO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "woi-grader-archive/ToolSmith")

async def gitUpload(file: UploadFile):
    with TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, file.filename)

        # Save uploaded zip file
        with open(zip_path, "wb") as f:
            f.write(await file.read())

        # Extract config.json to get title
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            config_filename = None
            for name in zip_ref.namelist():
                if name.endswith("config.json"):
                    config_filename = name
                    break

            if config_filename is None:
                raise ValueError("config.json not found in zip file")

            with zip_ref.open(config_filename) as config_file:
                config = json.load(config_file)
                folder_name = config.get("title", "untitled").strip().replace(" ", "_")

            dest_folder = os.path.join(REPO_PATH, folder_name)
            os.makedirs(dest_folder, exist_ok=True)

            # Extract all files into the destination folder
            zip_ref.extractall(dest_folder)

        # Convert any .md files to .pdf
        for root, _, files in os.walk(dest_folder):
            for name in files:
                if name.lower().endswith(".md"):
                    md_path = os.path.join(root, name)
                    pdf_path = os.path.splitext(md_path)[0] + ".pdf"
                    with open(md_path, "r", encoding="utf-8") as md_file:
                        md_content = md_file.read()
                    MD_PDF(md_content, pdf_path)

        # Git operations
        subprocess.run(["git", "add", "."], cwd=REPO_PATH, check=True)
        subprocess.run(["git", "commit", "-m", f"Upload from web UI: {file.filename} (as {folder_name})"], cwd=REPO_PATH, check=True)
        subprocess.run(["git", "push"], cwd=REPO_PATH, check=True)
