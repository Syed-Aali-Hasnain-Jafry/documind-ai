![DocuMind API Demo](screenshots/invoice-extraction.png)

# DocuMind AI


A document-processing API built using Python and FastAPI.

DocuMind extracts useful information from PDF and TXT documents and returns structured JSON data.

## Features

- Upload PDF and TXT documents
- Extract document text
- Detect email addresses
- Detect phone numbers
- Identify dates
- Extract invoice numbers
- Extract invoice amounts and currencies
- Validate uploads and handle errors
- Automated testing using pytest

## Tech Stack

- Python 3.11
- FastAPI
- Pydantic
- pypdf
- Regular Expressions
- pytest

## How It Works

1. User uploads a document.
2. FastAPI receives the file.
3. Python extracts the document text.
4. Regex identifies useful information.
5. Pydantic validates the response.
6. The API returns structured JSON.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/documind-ai.git
cd documind-ai
```

Create a virtual environment:

```bash
python -m venv .venv
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the server:

```bash
python -m uvicorn app.main:app --reload
```

Open:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /extract | Extract document information |

## Example Output

```json
{
  "emails": ["accounts@alienterprises.com"],
  "phone_numbers": ["+92 300 1234567"],
  "dates": ["2026-11-11", "2026-11-25"],
  "invoice_number": "INV-2026-1045",
  "total_amount": 50000.0,
  "currency": "PKR"
}
```

The example above shows the `fields` portion of the API response.

## Testing

Run:

```bash
python -m pytest -v
```

## Limitations

- Scanned PDFs require OCR.
- Invoice extraction currently depends on specific text patterns.
- This version does not use LLMs or autonomous agents.

## Future Improvements

- AI-powered document understanding
- OCR for scanned documents
- Support for more document types
- RAG-based document search
- Agentic document workflows

## Author

Syed Aali Hasnain Jafry

google-genai
```
