# core/services/pdf_service.py
import markdown
import pdfkit
import os

# HTML Template with CSS (no changes here)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'DejaVu Sans', 'Garuda', 'Tahoma', sans-serif;
            font-size: 16px;
            line-height: 1.6;
        }}
        h1, h2, h3 {{ font-weight: bold; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
            border: 1px solid #ddd;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
            vertical-align: top;
        }}
        th {{ background-color: #f2f2f2; }}
        code, pre {{
            font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 4px;
        }}
        pre {{ padding: 1rem; overflow-x: auto; }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""

class PdfService:
    def markdown_to_pdf_bytes(self, md_content: str) -> bytes:
        """
        Converts a markdown string into PDF content as bytes.
        """
        try:
            # The configuration is no longer needed, as pdfkit will find the installed tool.
            html_body = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
            full_html = HTML_TEMPLATE.format(html_body=html_body)
            
            options = {
                'encoding': "UTF-8",
                'custom-header': [('Content-Encoding', 'utf-8')],
                'no-outline': None
            }
            
            pdf_config = pdfkit.configuration(
                wkhtmltopdf=os.path.join(os.path.dirname(os.path.abspath(__file__)), "wkhtmltopdf/bin/wkhtmltopdf.exe")
            )
            # This call will now work correctly
            pdf_bytes = pdfkit.from_string(full_html, False, options=options, configuration=pdf_config)
            return pdf_bytes
            
        except Exception as e:
            print(f"Error during PDF conversion. Please ensure wkhtmltopdf is installed and accessible in your system's PATH. Error: {e}")
            raise Exception("Failed to convert Markdown to PDF. Is wkhtmltopdf installed?")

# Dependency Injection
def get_pdf_service():
    yield PdfService()