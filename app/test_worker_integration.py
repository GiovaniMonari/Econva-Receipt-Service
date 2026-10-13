import asyncio
from pathlib import Path

from app.clients.finance_client import FinanceClient
from app.services.receipt_extraction_service import (
    ReceiptExtractionService,
)
from app.services.receipt_parser_service import (
    ReceiptParserService,
)


async def main():
    receipt_id = input("Digite o receiptId: ").strip()

    extraction_service = ReceiptExtractionService()
    parser_service = ReceiptParserService()
    finance_client = FinanceClient()

    print("\nExecutando OCR...")

    extraction = await extraction_service.extract(
        Path("uploads/test-receipt.jpg")
    )

    print("OCR concluído.")

    parsed = parser_service.parse(
        extraction["rawText"]
    )

    print("\n===== DADOS EXTRAÍDOS =====")

    print(f"Estabelecimento: {parsed['merchant']}")
    print(f"Total: {parsed['total']}")
    print(f"Data: {parsed['date']}")
    print(f"Moeda: {parsed['currency']}")

    print("\nEnviando para NestJS...")

    result = await finance_client.process_receipt(
        receipt_id=receipt_id,
        data={
            "merchant": parsed["merchant"],
            "total": parsed["total"],
            "date": parsed["date"],
            "items": parsed["items"],
        },
    )

    print("\n===== RESPOSTA DO NESTJS =====")
    print(result)


asyncio.run(main())