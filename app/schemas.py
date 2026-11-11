"""Response schemas shared by the API and its clients."""
from pydantic import BaseModel, Field


class ExtractedFields(BaseModel):
    emails: list[str] = Field(default_factory=list)
    phone_numbers: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    invoice_number: str | None = None
    total_amount: float | None = None
    currency: str | None = None

     


class DocumentResult(BaseModel):
    filename: str
    document_type: str
    character_count: int = Field(ge=0)
    page_count: int = Field(ge=1)
    text: str
    fields: ExtractedFields
