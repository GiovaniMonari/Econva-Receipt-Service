import asyncio
from pathlib import Path

from app.services.receipt_extraction_service import (
    ReceiptExtractionService,
)
from app.services.receipt_parser_service import (
    ReceiptParserService,
)


async def main():
    extraction_service = ReceiptExtractionService()
    parser_service = ReceiptParserService()

    result = await extraction_service.extract(
        Path("uploads/test-receipt.jpg")
    )

    parsed = parser_service.parse(
        result["rawText"]
    )

    print("\n===== RESULTADO ESTRUTURADO =====\n")

    print(f"Estabelecimento: {parsed['merchant']}")
    print(f"Total: {parsed['total']}")
    print(f"Data: {parsed['date']}")
    print(f"Moeda: {parsed['currency']}")
    print(f"Confiança: {parsed['confidence']}")

    print("\nItens:")

    for item in parsed["items"]:
        print(item)


asyncio.run(main())