import os
import asyncio
from notion_manager import NotionManager
from dotenv import load_dotenv

async def check_hotel(hotel_name):
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("DATABASE_ID")

    if not token or not db_id:
        print("NOTION_TOKEN or DATABASE_ID not found in environment.")
        return

    mgr = NotionManager(token, db_id)

    # Query for the specific hotel name
    query_filter = {
        "property": "Name",
        "title": {
            "contains": hotel_name
        }
    }

    response = await mgr.notion.request(
        path=f"databases/{db_id.replace('-', '').strip()}/query",
        method="POST",
        body={"filter": query_filter}
    )

    results = response.get("results", [])
    if not results:
        print(f"Hotel '{hotel_name}' not found in Notion.")
        return

    hotel_page = results[0]
    hotel_data = mgr.extract_hotel_data(hotel_page)
    print(f"Found Hotel: {hotel_data}")
    return hotel_data

if __name__ == "__main__":
    asyncio.run(check_hotel("Quellenhof"))
