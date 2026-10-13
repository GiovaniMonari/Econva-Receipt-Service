from pathlib import Path

from app.clients.finance_client import FinanceClient
from app.services.receipt_extraction_service import (
    ReceiptExtractionService,
)
from app.services.receipt_parser_service import (
    ReceiptParserService,
)


class ReceiptWorker:
    """Orchestrates extract -> parse -> notify finance.

    Services are injectable so the API lifespan can share the
    heavy OCR singleton instead of loading the model twice.
    """

    def __init__(
        self,
        extraction_service: ReceiptExtractionService | None = None,
        parser_service: ReceiptParserService | None = None,
        finance_client: FinanceClient | None = None,
    ):
        self.extraction_service = (
            extraction_service or ReceiptExtractionService()
        )
        self.parser_service = parser_service or ReceiptParserService()
        self.finance_client = finance_client or FinanceClient()

    async def process(
        self,
        receipt_id: str,
        file_path: Path,
        authorization: str | None = None,
    ) -> dict:
        extraction = await self.extraction_service.extract(
            file_path
        )

        parsed = self.parser_service.parse(
            extraction["rawText"]
        )

        result = await self.finance_client.process_receipt(
            receipt_id=receipt_id,
            data={
                "merchant": parsed["merchant"],
                "total": parsed["total"],
                "date": parsed["date"],
                "items": parsed["items"],
            },
            authorization=authorization,
        )

        return result