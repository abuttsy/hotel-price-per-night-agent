import os
import asyncio
from notion_client import AsyncClient
from dotenv import load_dotenv

async def test_notion_search_exact():
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")

    client = AsyncClient(auth=token)

    try:
        response = await client.request(
            path="search",
            method="POST",
            body={
                "query": "Quellenhof"
            }
        )
        print(f"Found {len(response.get('results', []))} results.")
        for res in response.get('results', []):
            obj_type = res.get('object')
            if obj_type == 'page':
                props = res.get('properties', {})
                name_prop = props.get('Name', {}).get('title', [])
                name = name_prop[0].get('plain_text') if name_prop else 'Unknown'
                print(f"Page: {name}, ID: {res.get('id')}")
            elif obj_type == 'database':
                title_prop = res.get('title', [])
                title = title_prop[0].get('plain_text') if title_prop else 'Unknown'
                print(f"Database: {title}, ID: {res.get('id')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_notion_search_exact())
