import os
import asyncio
from notion_manager import NotionManager
from dotenv import load_dotenv
import httpx

async def find_quellenhof():
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    db_id = "58f6e6a92c684fe99100e9808b4e7e31"

    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    # Simple query to get all results
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json={})
        if response.status_code == 200:
            results = response.json().get("results", [])
            for page in results:
                props = page.get("properties", {})
                name_prop = props.get("Name", {}).get("title", [])
                name = name_prop[0].get("plain_text") if name_prop else "Unknown"
                if "Quellenhof" in name:
                    print(f"Found Quellenhof: {name}")
                    url_prop = props.get("URL", {}).get("url")
                    print(f"URL: {url_prop}")
                    return name, url_prop
            print("Quellenhof not found in the first 100 results.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    return None, None

if __name__ == "__main__":
    asyncio.run(find_quellenhof())
