from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from tempfile import SpooledTemporaryFile
from fastapi import UploadFile
from pydantic import BaseModel
from dotenv import load_dotenv

# init
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Load prompt
with open("prompt.txt", "r", encoding="utf-8") as f:
    structure = f.read()

# Call from API
class requestFromUser(BaseModel):
    content_name: str
    cases_size: int
    detail: str

async def generate_task(requestFromUser: requestFromUser) -> list[UploadFile]:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "คุณคือคนที่ต้องสร้างโจทย์ competetive programming โดยต้องทำตามโครงสร้างใน human message อย่างเคร่งครัด"),
        ("human", structure)
    ])
    chain = prompt | llm
    content_name = requestFromUser.content_name.lower().replace(" ", "_")
    cases_size = requestFromUser.cases_size
    detail = requestFromUser.detail
    res = await chain.ainvoke({"content": content_name, "casesSize": cases_size, "detail": detail})

    task_string = res.content.split("________________________________________")
    task_name = task_string[0].replace("\n", "").replace(" ", "")
    task_string.pop(0)

    for i in [0, 2, 3]: task_string[i] = backtickFilter(task_string[i])

    print(task_string[0])
    testcases = testcases_generate(task_string[0])

    task_files = []
    file_name = ["generate_input.py", "README.md", f"{task_name}.cpp", "config.json"]

    for file, name in zip(task_string, file_name):
        temp_file = SpooledTemporaryFile()
        temp_file.write(file.encode("utf-8"))
        temp_file.seek(0)
        task_files.append(UploadFile(filename=name, file=temp_file))

    input_files = []
    for i in range(0, len(testcases[0])):
        temp_file = SpooledTemporaryFile()
        temp_file.write(testcases[0][i].encode("utf-8"))
        temp_file.seek(0)
        input_files.append(UploadFile(filename="input/input"+str(i).zfill(2), file=temp_file))
    task_files.extend(input_files)

    output_files = []
    for i in range(0, len(testcases[1])):
        temp_file = SpooledTemporaryFile()
        temp_file.write(testcases[1][i].encode("utf-8"))
        temp_file.seek(0)
        output_files.append(UploadFile(filename="output/output"+str(i).zfill(2), file=temp_file))
    task_files.extend(output_files)

    return task_files

def testcases_generate(code: str) -> list[list[str], list[str]]:
    code = "import random\n" + code
    local_vars = {}
    exec(code, {}, local_vars)

    if "generate_test_cases" not in local_vars:
        raise ValueError("No function named generate_test_cases found in generated code.")

    generate_test_cases = local_vars["generate_test_cases"]
    test_input, test_output = generate_test_cases()

    return [test_input, test_output]

def backtickFilter(text):
    filtered_lines = [line for line in text.splitlines() if "```" not in line]
    result = "\n".join(filtered_lines)
    return result
