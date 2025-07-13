# core/graphs/nodes/file_creation.py
from core.models.graph_models import GraphState
from core.services.pdf_service import get_pdf_service # <-- Import service ใหม่
import re
import traceback
import random

def _clean_content(content: str) -> str:
    cleaned_content = re.sub(r'```(?:[a-z]+\n)?(.*?)\n?```', r'\1', content, flags=re.DOTALL)
    cleaned_content = cleaned_content.replace("TaskName:", "").replace("TaskName", "").strip()
    lines = cleaned_content.strip().split('\n')
    if lines and (lines[0].strip().endswith('.py') or re.match(r'^[a-zA-Z0-9_.-]+\.[a-zA-Z]+$', lines[0].strip())):
        lines.pop(0)
    return '\n'.join(lines).strip()

def _execute_generator(code: str, cases_size: int):
    local_vars = {}
    exec_globals = {'random': random, '__builtins__': __builtins__}
    exec(code, exec_globals, local_vars)
    if 'generate_test_cases' not in local_vars:
        raise ValueError("Function 'generate_test_cases' not found in generated code.")
    main_func = local_vars['generate_test_cases']
    exec_globals.update(local_vars)
    return main_func(cases_size)

async def create_files_node(state: GraphState) -> dict:
    """
    Parses LLM output, generates all files including PDF,
    and structures them for upload.
    """
    print("--- NODE: CREATING FILES (including PDF) ---")
    try:
        parts = state["llm_output"].split("________________________________________")
        if len(parts) != 5:
            raise ValueError(f"Expected 5 parts from LLM output, but got {len(parts)}.")
            
        task_name_raw = _clean_content(parts[0])
        gen_py = _clean_content(parts[1])
        readme_md = _clean_content(parts[2])
        solution = _clean_content(parts[3])
        config = _clean_content(parts[4])
        
        task_name = task_name_raw # ชื่อที่สะอาดแล้ว

        inputs, outputs = _execute_generator(gen_py, state["request"].cases_size)

        # --- ส่วนที่เพิ่มเข้ามาสำหรับการสร้าง PDF ---
        pdf_service = next(get_pdf_service())
        print(f"  Generating PDF for task: {task_name}")
        pdf_content_bytes = pdf_service.markdown_to_pdf_bytes(readme_md)
        # ----------------------------------------
        
        files = [
            {"category": "Solution", "file_path": f"Solutions/{task_name}.cpp", "file_name": f"{task_name}.cpp", "content": solution},
            {"category": "Problem", "file_path": f"Problems/{task_name}.md", "file_name": f"{task_name}.md", "content": readme_md},
            # --- เพิ่มไฟล์ PDF เข้าไปใน list ---
            {"category": "Problem", "file_path": f"Problems/{task_name}.pdf", "file_name": f"{task_name}.pdf", "content": pdf_content_bytes},
            {"category": "Config", "file_path": "config.json", "file_name": "config.json", "content": config},
            {"category": "Script", "file_path": "Scripts/generate.py", "file_name": "generate.py", "content": gen_py}
        ]
        
        for i, content in enumerate(inputs):
            file_name = f"input{i:02}.txt"
            files.append({"category": "TestCaseInput", "file_path": f"TestCases/Inputs/{file_name}", "file_name": file_name, "content": str(content)})
        
        for i, content in enumerate(outputs):
            file_name = f"output{i:02}.txt"
            files.append({"category": "TestCaseOutput", "file_path": f"TestCases/Outputs/{file_name}", "file_name": file_name, "content": str(content)})
        
        return {"task_name": task_name, "files": files}

    except Exception:
        raw_parts = state["llm_output"].split("________________________________________")
        problematic_code = raw_parts[1] if len(raw_parts) > 1 else "N/A"
        detailed_error = (
            f"An error occurred during file creation.\n"
            f"--- Full Traceback ---\n{traceback.format_exc()}\n"
            f"--- Problematic Python Code ---\n{_clean_content(problematic_code)}\n------------------------"
        )
        return {"error": detailed_error}