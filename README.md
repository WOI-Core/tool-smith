# **Toolsmith - AI-Powered Task Generator**

**Toolsmith** คือโปรเจกต์สำหรับสร้างชุดโจทย์ปัญหา Competitive Programming โดยอัตโนมัติ โดยใช้สถาปัตยกรรมสมัยใหม่ที่ประกอบด้วย FastAPI, LangGraph, และ Google Gemini API สำหรับการสร้างเนื้อหา และใช้ Supabase Storage ในการจัดเก็บไฟล์โจทย์ทั้งหมดอย่างเป็นระบบ

## **✨ Core Technologies**

  * **Backend**: FastAPI
  * **LLM Orchestration**: LangGraph
  * **LLM Model**: Google Gemini API
  * **File Storage**: Supabase Storage
  * **PDF Generation**: `wkhtmltopdf`
  * **Configuration**: Pydantic Settings

## **📂 Project Structure**

โปรเจกต์นี้แบ่งโครงสร้างออกเป็น 3 ส่วนหลักเพื่อความเป็นระเบียบ:

  * **/app**: ทำหน้าที่เป็น API Layer รับและตอบสนอง HTTP requests โดยตรง
  * **/core**: เป็นแกนหลักของแอปพลิเคชัน ประกอบด้วย Business Logic, Services, และการจัดการ Graph ทั้งหมด
  * **/static**: โฟลเดอร์สำหรับเก็บไฟล์คงที่ เช่น `favicon.ico`

## **🚀 การติดตั้งและเริ่มใช้งาน (Setup and Installation)**

ทำตามขั้นตอนต่อไปนี้เพื่อติดตั้งและรันโปรเจกต์บนเครื่องของคุณ

### **1. Clone a Project**

เริ่มต้นด้วยการ clone repository นี้ลงบนเครื่องของคุณ:

```bash
git clone <your-repository-url>
cd your_project_directory
```

### **2. ติดตั้ง System Dependencies (สำคัญมาก)**

โปรเจกต์นี้ต้องการ `wkhtmltopdf` สำหรับสร้างไฟล์ PDF คุณต้องติดตั้งมันลงบนระบบปฏิบัติการของคุณก่อน

  * **สำหรับ Linux (Debian/Ubuntu):**
    ```bash
    sudo apt-get update && sudo apt-get install wkhtmltopdf
    ```
  * **สำหรับ OS อื่นๆ:** โปรดดูวิธีการติดตั้งจาก [official wkhtmltopdf documentation](https://wkhtmltopdf.org/downloads.html)

### **3. สร้างโฟลเดอร์ `static`**

ที่ root ของโปรเจกต์ ให้สร้างโฟลเดอร์ใหม่ขึ้นมาชื่อว่า `static` และนำไฟล์ไอคอน (เช่น `favicon.ico`) ไปใส่ไว้ข้างใน

```bash
mkdir static
# (Optional) cp path/to/your/favicon.ico static/
```

### **4. สร้างและเปิดใช้งาน Virtual Environment**

เพื่อป้องกันปัญหาเรื่องเวอร์ชันของ Library ควรสร้างสภาพแวดล้อมเสมือน (Virtual Environment) ขึ้นมาใหม่:

```bash
# สำหรับ macOS/Linux
python3 -m venv venv
source venv/bin/activate

# สำหรับ Windows
python -m venv venv
.\venv\Scripts\activate
```

### **5. ติดตั้ง Python Dependencies**

ติดตั้ง Library ที่จำเป็นทั้งหมดจากไฟล์ `requirements.txt`:

```bash
pip install -r requirements.txt
```

### **6. ตั้งค่า Environment Variables**

สร้างไฟล์ `.env` ที่ root ของโปรเจกต์โดยคัดลอกเนื้อหาจากตัวอย่างด้านล่าง และกรอกข้อมูลของคุณลงไป:

```env
# .env
SUPABASE_URL="YOUR_SUPABASE_URL"
SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
```

  * `SUPABASE_URL` และ `SUPABASE_KEY`: สามารถหาได้จากหน้า Project Settings \> API ใน Dashboard ของ Supabase
  * `GOOGLE_API_KEY`: คือ API Key สำหรับใช้งาน Google Gemini

### **7. ตั้งค่า Supabase Storage**

ในโปรเจกต์ Supabase ของคุณ ให้ไปที่เมนู **Storage** ด้านซ้ายมือ แล้วทำตามขั้นตอนต่อไปนี้:

1.  คลิกที่ปุ่ม **"New bucket"**

2.  ในช่อง "Bucket name" ให้ตั้งชื่อว่า **`problems`**

3.  เปิดสวิตช์ **"Public bucket"** ให้เป็น On

4.  คลิกปุ่ม **"Create bucket"**

5.  ไปที่เมนู **Authentication** \> **Policies** และสร้าง Policy ใหม่สำหรับ Storage เพื่ออนุญาตการอัปโหลด

    **ใช้ SQL Editor รันคำสั่งนี้:**

    ```sql
    -- Policy นี้จะอนุญาตให้ทุกคนสามารถอัปโหลดไฟล์ (INSERT) ลงใน bucket 'problems' ได้
    CREATE POLICY "Allow public uploads to problems bucket"
    ON storage.objects FOR INSERT
    WITH CHECK ( bucket_id = 'problems' );
    ```

## **▶️ การรันแอปพลิเคชัน**

หลังจากตั้งค่าทุกอย่างเสร็จสิ้น สามารถรันเซิร์ฟเวอร์ FastAPI ได้ด้วยคำสั่ง:

```bash
uvicorn app.main:app --reload
```

เมื่อรันสำเร็จ คุณจะเห็นข้อความว่าแอปพลิเคชันทำงานอยู่ที่ `http://127.0.0.1:8000`

## **💻 ใช้งานโปรแกรม**

1.  **เปิดไฟล์ `index.html`** ในโฟลเดอร์ frontend ของคุณด้วย Web Browser
2.  กรอกรายละเอียดโจทย์ที่ต้องการ แล้วกดปุ่ม **"Generate Problem"**
3.  ระบบจะแสดงตัวอย่างไฟล์ที่สร้างได้ รวมถึงไฟล์ `.pdf`
4.  ตรวจสอบความถูกต้อง แล้วกดปุ่ม **"Approve and Upload to Database"** เพื่ออัปโหลดไฟล์ทั้งหมดไปยัง Supabase Storage Bucket ของคุณ
5.  สามารถกด **"Download ZIP"** เพื่อดาวน์โหลดไฟล์ทั้งหมดในรูปแบบไฟล์ ZIP ได้ตลอดเวลาหลังจากการ Generate สำเร็จ
