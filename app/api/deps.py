from fastapi import Request

from app.clients.finance_client import FinanceClient
from app.services.receipt_extraction_service import (
    ReceiptExtractionService,
)
from app.services.receipt_parser_service import ReceiptParserService


def get_finance_client(request: Request) -> FinanceClient:
    try:
        return request.app.state.finance_client
    except AttributeError:
        # Lifespan not run (e.g. plain TestClient without context).
        return FinanceClient()


def get_extraction_service(request: Request) -> ReceiptExtractionService:
    try:
        return request.app.state.extraction_service
    except AttributeError:
        return ReceiptExtractionService()


def get_parser_service(request: Request) -> ReceiptParserService:
    try:
        return request.app.state.parser_service
    except AttributeError:
        return ReceiptParserService()
