from fastapi import UploadFile
import os
import zipfile
import json
from tempfile import TemporaryDirectory
import shutil
import subprocess
from MD_PDF import MD_PDF

REPO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "woi-grader-archive/ToolSmith")

async def gitUpload(file: UploadFile):
    with TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, file.filename)

        # Save uploaded zip file
        with open(zip_path, "wb") as f:
            f.write(await file.read())

        # เปิด zip อ่าน config.json และ title
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

            # แตกไฟล์ทั้งหมดไปโฟลเดอร์ชั่วคราวก่อน
            tmp_extract_folder = os.path.join(tmpdir, "extracted")
            os.makedirs(tmp_extract_folder)
            zip_ref.extractall(tmp_extract_folder)

        # สร้างโฟลเดอร์โครงสร้างตามต้องการใน dest_folder
        problems_folder = os.path.join(dest_folder, "Problems")
        testcases_inputs_folder = os.path.join(dest_folder, "TestCases", "Inputs")
        testcases_outputs_folder = os.path.join(dest_folder, "TestCases", "Outputs")
        solutions_folder = os.path.join(dest_folder, "Solutions")

        for path in [problems_folder, testcases_inputs_folder, testcases_outputs_folder, solutions_folder]:
            os.makedirs(path, exist_ok=True)

        # หาไฟล์ .md ตัวแรกใน tmp_extract_folder เพื่อใช้แปลง pdf และก็ย้ายไป Problems
        md_file_path = None
        for root, _, files in os.walk(tmp_extract_folder):
            for name in files:
                if name.lower().endswith(".md"):
                    md_file_path = os.path.join(root, name)
                    break
            if md_file_path:
                break

        if md_file_path:
            # ย้าย .md ไป Problems/(title).md
            md_dest_path = os.path.join(problems_folder, f"{folder_name}.md")
            shutil.copy2(md_file_path, md_dest_path)

            # แปลง pdf และเก็บใน Problems/(title).pdf
            pdf_path = os.path.join(problems_folder, f"{folder_name}.pdf")
            with open(md_file_path, "r", encoding="utf-8") as md_file:
                md_content = md_file.read()
            MD_PDF(md_content, pdf_path)

        # ย้ายไฟล์ config.json ไปโฟลเดอร์หลัก
        config_src_path = os.path.join(tmp_extract_folder, config_filename)
        config_dest_path = os.path.join(dest_folder, "config.json")
        shutil.copy2(config_src_path, config_dest_path)

        # ย้ายไฟล์ input*.txt ไป TestCases/Inputs
        for root, _, files in os.walk(tmp_extract_folder):
            for name in files:
                if name.startswith("input") and name.endswith(".txt"):
                    src = os.path.join(root, name)
                    dst = os.path.join(testcases_inputs_folder, name)
                    shutil.copy2(src, dst)

        # ย้ายไฟล์ output*.txt ไป TestCases/Outputs
        for root, _, files in os.walk(tmp_extract_folder):
            for name in files:
                if name.startswith("output") and name.endswith(".txt"):
                    src = os.path.join(root, name)
                    dst = os.path.join(testcases_outputs_folder, name)
                    shutil.copy2(src, dst)

        # ย้ายไฟล์ .cpp ทั้งหมดไป Solutions
        for root, _, files in os.walk(tmp_extract_folder):
            for name in files:
                if name.lower().endswith(".cpp"):
                    src = os.path.join(root, name)
                    dst = os.path.join(solutions_folder, name)
                    shutil.copy2(src, dst)

        # ทำ git add, commit, push
        subprocess.run(["git", "add", "."], cwd=REPO_PATH, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"From Tool Smith: {file.filename} (as {folder_name})"],
            cwd=REPO_PATH,
            check=True
        )
        subprocess.run(["git", "push"], cwd=REPO_PATH, check=True)
