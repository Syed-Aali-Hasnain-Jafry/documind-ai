"""Unit tests for the extraction logic."""
import pytest

from app.extractor import extract_fields, read_document


def test_extract_fields_deduplicates():
    fields = extract_fields("one@example.org one@example.org 2026-11-11 2026-11-11")
    assert fields.emails == ["one@example.org"]
    assert fields.dates == ["2026-11-11"]


def test_reads_utf8_with_bom():
    text, pages = read_document(b"\xef\xbb\xbfHello", ".txt")
    assert text == "Hello"
    assert pages == 1


def test_rejects_unknown_type():
    with pytest.raises(ValueError, match="Unsupported"):
        read_document(b"data", ".docx")

def test_date_not_detected_as_phone():
    from app.extractor import extract_fields

    text = (
        "Email: aali@example.com\n"
        "Phone: +92 333 1234567\n"
        "Date: 2026-11-11"
    )

    result = extract_fields(text)

    assert result.emails == ["aali@example.com"]
    assert result.phone_numbers == ["+92 333 1234567"]
    assert result.dates == ["2026-11-11"]



def test_invoice_extraction():
    from app.extractor import extract_fields

    text = """
    INVOICE
    Company: TechNova Solutions
    Invoice Number: INV-2026-1045
    Total Amount: PKR 50000
    """

    result = extract_fields(text)

    assert result.invoice_number == "INV-2026-1045"
    assert result.total_amount == 50000.0
    assert result.currency == "PKR"
