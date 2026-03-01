import os
import asyncio
from notion_client import AsyncClient
from dotenv import load_dotenv

async def test_notion():
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("DATABASE_ID")

    client = AsyncClient(auth=token)

    try:
        # Just try to retrieve the database first
        response = await client.request(
            path=f"databases/{db_id}",
            method="GET"
        )
        print("Database found!")
        print(f"Title: {response.get('title', [{}])[0].get('plain_text', 'No Title')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_notion())
