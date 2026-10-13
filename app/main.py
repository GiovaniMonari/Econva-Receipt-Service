import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.receipts import router as receipts_router
from app.clients.finance_client import FinanceClient
from app.services.receipt_extraction_service import (
    ReceiptExtractionService,
)
from app.services.receipt_parser_service import ReceiptParserService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Singletons shared via app.state + app/api/deps.py.
    # Extraction holds the heavy PaddleOCR model: one instance
    # per process, lazily loaded on first use.
    app.state.finance_client = FinanceClient()
    app.state.extraction_service = ReceiptExtractionService()
    app.state.parser_service = ReceiptParserService()
    logger.info("receipt service started")
    yield


app = FastAPI(
    title="Econva Receipt Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(receipts_router, prefix="/receipts", tags=["Receipts"])


@app.get("/health")
def health():
    return {"status": "ok"}