import markdown
import pdfkit
from fastapi import UploadFile
from tempfile import SpooledTemporaryFile
import os

config = pdfkit.configuration(wkhtmltopdf=os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "wkhtmltopdf/bin/wkhtmltopdf.exe"
))

def MD_PDF(md: str, name: str) -> UploadFile:
    html_body = markdown.markdown(md, extensions=['tables', 'fenced_code'])

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
            h1, h2, h3 {{ font-weight: bold; }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 10px 0;
            }}
            table, th, td {{
                border: 1px solid black;
                padding: 8px;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: monospace;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
    {html_body}
    </body>
    </html>
    """

    tmp_pdf = SpooledTemporaryFile(suffix=".pdf", mode="w+b")
    pdfkit.from_string(html_template, tmp_pdf, configuration=config, options={
        'encoding': 'utf-8'
    })
    tmp_pdf.seek(0)
    return UploadFile(filename=name + ".pdf", file=tmp_pdf, content_type="application/pdf")
