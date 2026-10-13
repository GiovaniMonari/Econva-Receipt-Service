import asyncio
from pathlib import Path

from app.workers.receipt_worker import ReceiptWorker


async def main():
    worker = ReceiptWorker()

    result = await worker.process(
        receipt_id="test-receipt",
        file_path=Path("uploads/test-receipt.jpg"),
    )

    print("\n===== WORKER RESULT =====\n")

    print(f"Receipt ID: {result['receiptId']}")

    print("\nDados estruturados:")

    print(f"Estabelecimento: {result['data']['merchant']}")
    print(f"Total: {result['data']['total']}")
    print(f"Data: {result['data']['date']}")
    print(f"Moeda: {result['data']['currency']}")

    print("\nItens:")

    for item in result["data"]["items"]:
        print(item)


asyncio.run(main())