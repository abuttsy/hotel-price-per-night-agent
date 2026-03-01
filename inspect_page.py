import os
import asyncio
from notion_client import AsyncClient
from dotenv import load_dotenv

async def inspect_page(page_id):
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    client = AsyncClient(auth=token)

    try:
        response = await client.request(
            path=f"pages/{page_id}",
            method="GET"
        )
        print(f"Page Object: {response.get('object')}")
        props = response.get('properties', {})
        for prop_name, prop_data in props.items():
            print(f"Property: {prop_name}, Type: {prop_data.get('type')}")
            if prop_data.get('type') == 'title':
                print(f"  Value: {prop_data.get('title', [{}])[0].get('plain_text')}")
            elif prop_data.get('type') == 'url':
                print(f"  Value: {prop_data.get('url')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_page("f7997be9-b6d0-44f2-bc37-8b54f679dc13"))
