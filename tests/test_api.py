"""Integration tests for the HTTP boundary."""
from io import BytesIO

from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.main import MAX_FILE_BYTES, app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_text_upload_extracts_fields():
    text = b"Email: hello@example.com\nDate: 2026-11-11\nPhone: +92 300 1234567"
    response = client.post("/extract", files={"file": ("example.txt", text, "text/plain")})
    assert response.status_code == 200
    payload = response.json()
    assert payload["document_type"] == "txt"
    assert payload["fields"]["emails"] == ["hello@example.com"]
    assert payload["fields"]["dates"] == ["2026-11-11"]
    assert payload["character_count"] == len(text.decode("utf-8"))


def test_rejects_unsupported_extension():
    response = client.post("/extract", files={"file": ("image.jpg", b"abc", "image/jpeg")})
    assert response.status_code == 415


def test_rejects_empty_upload():
    response = client.post("/extract", files={"file": ("empty.txt", b"", "text/plain")})
    assert response.status_code == 400


def test_rejects_large_upload():
    response = client.post("/extract", files={"file": ("large.txt", b"a" * (MAX_FILE_BYTES + 1), "text/plain")})
    assert response.status_code == 413


def test_rejects_non_utf8_txt():
    response = client.post("/extract", files={"file": ("bad.txt", b"\xff\xfe", "text/plain")})
    assert response.status_code == 422


def test_rejects_fake_pdf():
    response = client.post("/extract", files={"file": ("fake.pdf", b"not a pdf", "application/pdf")})
    assert response.status_code == 400


def test_rejects_pdf_with_no_extractable_text():
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = BytesIO()
    writer.write(buffer)
    response = client.post("/extract", files={"file": ("blank.pdf", buffer.getvalue(), "application/pdf")})
    assert response.status_code == 422
    assert "OCR" in response.json()["detail"]



def test_ai_invoice_endpoint(monkeypatch):
    from app.ai_extractor import InvoiceData

    # Fake Gemini response
    def fake_ai_extraction(text):
        return InvoiceData(
            invoice_number="INV-2026-1045",
            company="TechNova Solutions",
            total_amount=50000.0,
            currency="PKR",
        )

    # Replace the real AI function with our fake one
    monkeypatch.setattr(
        "app.main.extract_invoice_with_ai",
        fake_ai_extraction
    )

    # Upload a fake invoice
    response = client.post(
        "/extract/ai",
        files={
            "file": (
                "invoice.txt",
                b"Invoice Number: INV-2026-1045",
                "text/plain"
            )
        }
    )

    # Check the result
    assert response.status_code == 200

    data = response.json()

    assert data["invoice_number"] == "INV-2026-1045"
    assert data["company"] == "TechNova Solutions"
    assert data["total_amount"] == 50000.0
    assert data["currency"] == "PKR"
