from pathlib import Path

import asyncio

from paddleocr import PaddleOCR

from app.core.config import settings


class ReceiptExtractionService:
    """OCR-only service: returns raw text + confidence.

    Structured fields (merchant/total/date/items) are filled by
    ReceiptParserService in the next pipeline step.
    """

    def __init__(self, ocr: PaddleOCR | None = None):
        self._ocr = ocr

    @property
    def ocr(self) -> PaddleOCR:
        # Lazy singleton: avoids loading the model on import and
        # avoids re-loading it per request.
        if self._ocr is None:
            self._ocr = PaddleOCR(
                lang=settings.ocr_lang,
                enable_mkldnn=False,
            )
        return self._ocr

    def extract_sync(self, file_path: Path) -> dict:
        result = self.ocr.predict(str(file_path))

        raw_text: list[str] = []
        scores: list[float] = []

        for page in result:
            if not page:
                continue

            texts = page.get("rec_texts", [])
            page_scores = page.get("rec_scores", [])

            for i, text in enumerate(texts):
                if text:
                    raw_text.append(text)
                    if i < len(page_scores):
                        try:
                            scores.append(float(page_scores[i]))
                        except (TypeError, ValueError):
                            pass

        confidence = sum(scores) / len(scores) if scores else 0

        return {
            "rawText": "\n".join(raw_text),
            "confidence": confidence,
            "merchant": None,
            "total": None,
            "date": None,
            "currency": "BRL",
            "items": [],
        }

    async def extract(self, file_path: Path) -> dict:
        # PaddleOCR is blocking: never run it on the event loop.
        return await asyncio.to_thread(self.extract_sync, file_path)