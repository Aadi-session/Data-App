import io
import markdown


def md_to_html(md_text: str) -> str:
    """Convert markdown to a full HTML document with print-friendly CSS."""
    body_html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc"],
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 2cm 2.5cm;
  }}
  body {{
    font-family: "PP Neue Montreal", "Inter", "DM Sans", -apple-system,
                 BlinkMacSystemFont, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #242321;
  }}
  h1 {{
    font-size: 22pt;
    margin-top: 1.5em;
    color: #242321;
    letter-spacing: -0.02em;
  }}
  h2 {{
    font-size: 16pt;
    margin-top: 1.3em;
    border-bottom: 2px solid #54DED1;
    padding-bottom: 4px;
    color: #242321;
  }}
  h3 {{ font-size: 13pt; margin-top: 1em; color: #35505B; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 10pt;
  }}
  th, td {{
    border: 1px solid #c5bfb8;
    padding: 6px 10px;
    text-align: left;
  }}
  th {{
    background: #202F36;
    color: #EDE9E5;
    font-weight: 600;
  }}
  tr:nth-child(even) {{ background: #f3f0ec; }}
  code {{
    background: #E0DBD6;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 10pt;
    color: #35505B;
  }}
  ul, ol {{ padding-left: 1.5em; }}
  li {{ margin-bottom: 0.3em; }}
  hr {{ border: none; border-top: 1px solid #c5bfb8; margin: 1.5em 0; }}
  blockquote {{
    border-left: 3px solid #54DED1;
    margin: 1em 0;
    padding: 0.5em 1em;
    color: #35505B;
    background: #f3f0ec;
  }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""


def render_pdf_bytes(md_text: str) -> bytes | None:
    """Render markdown to PDF bytes. Returns None if weasyprint is unavailable."""
    try:
        from weasyprint import HTML
    except ImportError:
        return None

    html_str = md_to_html(md_text)
    buf = io.BytesIO()
    HTML(string=html_str).write_pdf(buf)
    return buf.getvalue()
