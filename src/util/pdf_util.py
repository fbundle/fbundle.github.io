import re
from datetime import datetime

import pymupdf


def get_pdf_dates(pdf_path: str) -> tuple[datetime, datetime]:
    def parse_pdf_date(date_str: str) -> datetime | None:
        if not date_str:
            return None
        if date_str.startswith("D:"):
            date_str = date_str[2:]  # Strip leading "D:" if present
        date_str = re.sub(r"[+-].*", "", date_str)  # Remove the timezone part like +08'00'
        dt = datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")  # Parse the date
        return dt

    doc = pymupdf.Document(pdf_path)
    creation_date = parse_pdf_date(doc.metadata.get("creationDate"))
    modified_date = parse_pdf_date(doc.metadata.get("modDate"))
    if creation_date is None:
        creation_date = datetime.min
    if modified_date is None:
        modified_date = datetime.min

    return creation_date, modified_date


def get_pdf_text(pdf_path: str) -> str:
    print(f"DEBUG: Extracting text from {pdf_path}")
    doc = pymupdf.Document(pdf_path)
    text_content = ""

    for page_num in range(len(doc)):
        try:
            page_text = doc[page_num].get_text()
            text_content += page_text + " "
        except Exception as e:
            print(f"DEBUG: Error on page {page_num}: {e}")
            continue

    doc.close()

    # Clean up text: remove extra whitespace and normalize
    import re
    text_content = re.sub(r'\s+', ' ', text_content).strip()

    print(f"DEBUG: Extracted {len(text_content)} characters from {pdf_path}")
    return text_content