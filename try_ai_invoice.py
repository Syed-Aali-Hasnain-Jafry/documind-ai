
from pathlib import Path

from app.ai_extractor import extract_invoice_with_ai


# Read our sample invoice
text = Path(
    "samples/invoice.txt"
).read_text(encoding="utf-8")

# Ask Gemini to understand it
result = extract_invoice_with_ai(text)

# Display the extracted information
print(result.model_dump_json(indent=2))
