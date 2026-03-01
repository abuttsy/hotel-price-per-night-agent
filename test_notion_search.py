import os
import asyncio
from notion_client import AsyncClient
from dotenv import load_dotenv

async def test_notion_search():
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")

    client = AsyncClient(auth=token)

    try:
        response = await client.request(
            path="search",
            method="POST",
            body={}
        )
        print(f"Found {len(response.get('results', []))} databases.")
        for db in response.get('results', []):
            title = db.get('title', [{}])[0].get('plain_text', 'No Title')
            print(f"Database: {title}, ID: {db.get('id')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_notion_search())
