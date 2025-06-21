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
class contentFromUser(BaseModel):
    content_name: str

async def generate_task(contentFromUser: contentFromUser) -> list[UploadFile]:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "คุณคือคนที่ต้องสร้างโจทย์ competetive programming โดยต้องทำตามโครงสร้างใน human message อย่างเคร่งครัด"),
        ("human", structure)
    ])
    chain = prompt | llm
    content_name = contentFromUser.content_name.lower().replace(" ", "_")
    res = await chain.ainvoke({"content": content_name, "casesNum": 10})

    taskfile = res.content.split("________________________________________")
    task_name = taskfile[0].replace("\n", "").replace(" ", "")
    taskfile.pop(0)

    task_files = []
    file_name = ["generate_input.py", "README.md", f"{task_name}.cpp"]

    for file, name in zip(taskfile, file_name):
        temp_file = SpooledTemporaryFile()
        temp_file.write(file.encode("utf-8"))
        temp_file.seek(0)
        task_files.append(UploadFile(filename=name, file=temp_file))

    return task_files