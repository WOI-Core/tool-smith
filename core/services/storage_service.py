# core/services/storage_service.py
from supabase import create_client, Client
from .config import settings
from typing import List, Dict, Union

class StorageService:
    def __init__(self, client: Client):
        self.client = client
        self.bucket_name = "problems"

    def upload_files(self, task_name: str, files: List[Dict]):
        """
        Uploads a list of files to the specified Supabase Storage bucket.
        The content can be either string or bytes.
        """
        try:
            print(f"Starting upload for task: {task_name} to bucket: {self.bucket_name}")
            
            for file_info in files:
                upload_path = f"{task_name}/{file_info['file_path']}"
                content_to_upload = file_info['content']

                # --- ตรวจสอบชนิดข้อมูลของ content ---
                file_content_bytes: bytes
                content_type = "text/plain;charset=utf-8" # Default

                if isinstance(content_to_upload, str):
                    # ถ้าเป็น string ให้ encode เป็น bytes
                    file_content_bytes = content_to_upload.encode('utf-8')
                elif isinstance(content_to_upload, bytes):
                    # ถ้าเป็น bytes อยู่แล้ว ให้ใช้ได้เลย
                    file_content_bytes = content_to_upload
                    # ถ้าเป็น PDF ให้เปลี่ยน content type
                    if file_info['file_name'].endswith('.pdf'):
                        content_type = "application/pdf"
                else:
                    # หากเป็นชนิดข้อมูลอื่นที่ไม่รองรับ ให้ข้ามไป
                    print(f"  Skipping unsupported content type for: {upload_path}")
                    continue
                # -----------------------------------

                print(f"  Uploading: {upload_path} ({content_type})")
                
                self.client.storage.from_(self.bucket_name).upload(
                    path=upload_path,
                    file=file_content_bytes,
                    file_options={"content-type": content_type}
                )

            print(f"Successfully uploaded {len(files)} files for task '{task_name}'.")

        except Exception as e:
            error_message = str(e)
            if "Duplicate" in error_message:
                print(f"Upload failed: A file with the same path already exists for task '{task_name}'.")
                raise Exception(f"Duplicate files found for task '{task_name}'.")
            
            print(f"Storage upload failed: {e}")
            raise e

def get_storage_service():
    client = create_client(settings.supabase_url, settings.supabase_key)
    yield StorageService(client)