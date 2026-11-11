
"""Pure document-processing functions, isolated from the HTTP layer."""

import re
from io import BytesIO

from pypdf import PdfReader

from app.schemas import ExtractedFields


# Regular expressions for extracting information
EMAIL = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE = re.compile(
    r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)"
)

ISO_DATE = re.compile(
    r"\b\d{4}-\d{2}-\d{2}\b"
)


def read_document(data: bytes, extension: str) -> tuple[str, int]:
    """Return text and page count for PDF or UTF-8 TXT files."""

    if extension == ".txt":
        try:
            return data.decode("utf-8-sig"), 1

        except UnicodeDecodeError as exc:
            raise ValueError(
                "TXT files must use UTF-8 encoding"
            ) from exc

    if extension == ".pdf":
        try:
            reader = PdfReader(BytesIO(data))

            if reader.is_encrypted:
                raise ValueError(
                    "Encrypted PDFs are not supported"
                )

            if not reader.pages:
                raise ValueError(
                    "PDF contains no pages"
                )

            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

            if not text.strip():
                raise ValueError(
                    "No selectable text found; scanned PDFs need OCR"
                )

            return text, len(reader.pages)

        except ValueError:
            raise

        except Exception as exc:
            raise ValueError(
                "Invalid or unreadable PDF"
            ) from exc

    raise ValueError("Unsupported document type")



def extract_fields(text: str) -> ExtractedFields:
    """Extract useful information from documents."""

    # 1. Find emails
    emails = list(dict.fromkeys(EMAIL.findall(text)))

    # 2. Find dates
    dates = list(dict.fromkeys(ISO_DATE.findall(text)))

    # 3. Find phone numbers
    phone_numbers = list(dict.fromkeys(PHONE.findall(text)))

    # Remove dates incorrectly detected as phone numbers
    phone_numbers = [
        phone
        for phone in phone_numbers
        if phone.strip() not in dates
    ]

    # 4. Find invoice number
    invoice_match = re.search(
        r"Invoice Number:\s*([A-Za-z0-9-]+)",
        text,
        re.IGNORECASE
    )

    invoice_number = (
        invoice_match.group(1)
        if invoice_match
        else None
    )

    # 5. Find total amount and currency
    amount_match = re.search(
        r"Total Amount:\s*([A-Z]{3})\s*([\d,]+(?:\.\d{1,2})?)",
        text,
        re.IGNORECASE
    )

    currency = (
        amount_match.group(1).upper()
        if amount_match
        else None
    )

    total_amount = (
        float(amount_match.group(2).replace(",", ""))
        if amount_match
        else None
    )

    # 6. Return the extracted information
    return ExtractedFields(
        emails=emails,
        phone_numbers=phone_numbers,
        dates=dates,
        invoice_number=invoice_number,
        total_amount=total_amount,
        currency=currency,
    )
