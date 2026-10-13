import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import (
    get_extraction_service,
    get_finance_client,
)
from app.clients.finance_client import FinanceClient
from app.core.config import settings
from app.schemas.receipts import ScanReceiptResponse
from app.services.receipt_extraction_service import (
    ReceiptExtractionService,
)

router = APIRouter()

security = HTTPBearer()


@router.post("/scan", response_model=ScanReceiptResponse)
async def scan_receipt(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    finance_client: FinanceClient = Depends(get_finance_client),
    extraction_service: ReceiptExtractionService = Depends(
        get_extraction_service
    ),
):
    authorization = f"{credentials.scheme} {credentials.credentials}"

    if file.content_type not in settings.allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo não suportado.",
        )

    content = await file.read()

    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail="Arquivo muito grande. Limite de 10MB.",
        )

    settings.upload_dir.mkdir(exist_ok=True)

    extension = Path(file.filename or "").suffix.lower()

    filename = f"{uuid4()}{extension}"
    file_path = settings.upload_dir / filename

    # Blocking disk write: keep it off the event loop.
    await asyncio.to_thread(file_path.write_bytes, content)

    image_url = f"/uploads/{filename}"

    receipt = await finance_client.create_receipt(
        image_url=image_url,
        authorization=authorization,
    )

    extracted_data = await extraction_service.extract(file_path)

    return {
        "message": "Recibo recebido com sucesso.",
        "receiptId": receipt["id"],
        "status": receipt["status"],
        "filename": filename,
        "originalName": file.filename,
        "mimeType": file.content_type,
        "size": len(content),
        "extractedData": extracted_data,
    }