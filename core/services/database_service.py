# core/services/database_service.py
from supabase import create_client, Client
from .config import settings
from core.models.pydantic_models import TaskRequest
from typing import List, Dict

class DatabaseService:
    def __init__(self, client: Client):
        self.client = client

    def create_task_record(self, req: TaskRequest, task_name: str, files: List[Dict]):
        """
        Inserts a main task record, then inserts all associated files
        into the respective tables.
        """
        try:
            # 1. สร้าง "โจทย์หลัก" ในตาราง tasks และดึง id ที่สร้างใหม่กลับมา
            task_record_data = {
                "name": task_name,
                "topic": req.content_name,
                "description": req.detail
            }
            # .execute() ใน v1 จะคืนค่า list ของ record ที่ถูก insert ใน data[1]
            inserted_task_data, count = self.client.table("tasks").insert(task_record_data).execute()
            
            if not inserted_task_data[1]:
                raise Exception("Failed to create main task record or retrieve its ID.")
            
            task_id = inserted_task_data[1][0]['id']
            print(f"Created main task '{task_name}' with ID: {task_id}")

            # 2. เตรียมข้อมูลไฟล์ทั้งหมดสำหรับตาราง task_files
            files_to_insert = []
            for file_info in files:
                files_to_insert.append({
                    "task_id": task_id,
                    "category": file_info['category'],
                    "file_path": file_info['file_path'],
                    "file_name": file_info['file_name'],
                    "file_content": file_info['content']
                })
            
            # 3. Insert ไฟล์ทั้งหมดลงในตาราง task_files ในครั้งเดียว
            if files_to_insert:
                self.client.table("task_files").insert(files_to_insert).execute()
            
            print(f"Successfully inserted {len(files_to_insert)} files for task ID: {task_id}")

        except Exception as e:
            print(f"Database insert failed: {e}")
            # (ทางเลือก) หากต้องการให้ API แจ้ง error กลับไป ต้อง raise exception
            raise e

def get_database_service():
    client = create_client(settings.supabase_url, settings.supabase_key)
    yield DatabaseService(client)