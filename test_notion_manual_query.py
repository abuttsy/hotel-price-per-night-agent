import os
import asyncio
from notion_client import AsyncClient
from dotenv import load_dotenv
import httpx

async def test_notion_manual_query():
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    db_id = "4c1a76c312d3402d9d83a255c3ae95aa"

    # Manually construct request
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as hclient:
        response = await hclient.post(url, headers=headers, json={})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Results: {len(data.get('results', []))}")
            for res in data.get('results', []):
                props = res.get('properties', {})
                name_list = props.get('Name', {}).get('title', [])
                name = name_list[0].get('plain_text') if name_list else 'No Name'
                print(f"Hotel: {name}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_notion_manual_query())
