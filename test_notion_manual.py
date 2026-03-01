import os
import asyncio
from notion_client import AsyncClient
from dotenv import load_dotenv

async def test_notion_manual():
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("DATABASE_ID").replace("-", "")

    client = AsyncClient(auth=token)

    try:
        # Manually construct request
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        import httpx
        async with httpx.AsyncClient() as hclient:
            response = await hclient.post(url, headers=headers, json={})
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("Success!")
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_notion_manual())
