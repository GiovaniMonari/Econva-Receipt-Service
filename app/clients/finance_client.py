import httpx

from app.core.config import settings


class FinanceClient:

    async def create_receipt(
        self,
        image_url: str,
        authorization: str,
    ):
        url = f"{settings.finance_service_url}/receipts/internal"

        payload = {
            "imageUrl": image_url,
        }

        headers = {
            "Authorization": authorization,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=settings.finance_create_timeout,
            )

        response.raise_for_status()

        return response.json()

    async def process_receipt(
        self,
        receipt_id: str,
        data: dict,
        authorization: str | None = None,
    ):
        url = (
            f"{settings.finance_service_url}"
            f"/receipts/internal/{receipt_id}/process"
        )

        headers = (
            {"Authorization": authorization}
            if authorization
            else None
        )

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                url,
                json=data,
                headers=headers,
                timeout=settings.finance_process_timeout,
            )

        response.raise_for_status()

        return response.json()