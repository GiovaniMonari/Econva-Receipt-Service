import asyncio
from pathlib import Path

from app.services.receipt_extraction_service import (
    ReceiptExtractionService,
)


async def main():
    service = ReceiptExtractionService()

    result = await service.extract(
        Path("uploads/test-receipt.jpg")
    )

    print("\n===== OCR =====\n")
    print(result["rawText"])


asyncio.run(main())