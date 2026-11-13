
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel


# Define what information AI should return
class InvoiceData(BaseModel):
    invoice_number: str | None
    company: str | None
    total_amount: float | None
    currency: str | None


def extract_invoice_with_ai(text: str) -> InvoiceData:
    """Ask Gemini to extract invoice details."""

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key is missing")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
           model="gemini-3.1-flash-lite",
            contents=(
                "Extract invoice details from the document below. "
                "Use null for missing information. "
                "Do not invent values.\n\n"
                f"DOCUMENT:\n{text}"
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InvoiceData,
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response")

        return InvoiceData.model_validate_json(response.text)

    finally:
        client.close()

