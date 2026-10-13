from pydantic import BaseModel


class ExtractedData(BaseModel):
    rawText: str
    confidence: float = 0
    merchant: str | None = None
    total: float | None = None
    date: str | None = None
    currency: str = "BRL"
    items: list[dict] = []


class ScanReceiptResponse(BaseModel):
    message: str = "Recibo recebido com sucesso."
    receiptId: str
    status: str
    filename: str
    originalName: str | None = None
    mimeType: str | None = None
    size: int
    extractedData: ExtractedData
