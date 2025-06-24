import markdown
import os
import pdfkit

# กำหนด path แบบถูกต้อง (แก้ให้เป็น raw string)
config = pdfkit.configuration(wkhtmltopdf=os.path.join(os.path.dirname(os.path.abspath(__file__)), "wkhtmltopdf/bin/wkhtmltopdf.exe"))

def MD_PDF(md: str, output_pdf: str = "output.pdf"):
    # รองรับ markdown + inline HTML เช่น <table>
    html_body = markdown.markdown(md, extensions=["extra"])

    html_template = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Tahoma, 'DejaVu Sans', sans-serif;
                font-size: 16px;
                line-height: 1.6;
            }}
            h1, h2, h3 {{
                font-weight: bold;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 16px 0;
            }}
            th, td {{
                border: 1px solid #666;
                padding: 8px 12px;
                text-align: left;
                vertical-align: top;  /* ✅ จัดให้ชิดบน */
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
        </style>
    </head>
    <body>
    {html_body}
    </body>
    </html>
    """

    pdfkit.from_string(html_template, output_pdf, configuration=config, options={
        'encoding': 'utf-8'
    })

# ตัวอย่างเรียกใช้
if __name__ == "__main__":
    with open("example.md", "r", encoding="utf-8") as f:
        md_text = f.read()
    MD_PDF(md_text)
