import os
import asyncio
from datetime import datetime, timedelta
from notion_client import AsyncClient
from typing import List, Dict, Any, Optional

class NotionManager:
    def __init__(self, token: str, database_id: str):
        self.notion = AsyncClient(auth=token)
        self.database_id = database_id

    async def get_hotels_to_update(self) -> List[Dict[str, Any]]:
        """
        Fetches hotels that either have no 'price last updated' or were updated more than 365 days ago.
        """
        hotels = []
        has_more = True
        start_cursor = None

        one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        query_filter = {
            "or": [
                {
                    "property": "price last updated",
                    "date": {
                        "is_empty": True
                    }
                },
                {
                    "property": "price last updated",
                    "date": {
                        "before": one_year_ago
                    }
                }
            ]
        }

        while has_more:
            response = await self.notion.databases.query(
                database_id=self.database_id,
                filter=query_filter,
                start_cursor=start_cursor
            )
            hotels.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return hotels

    async def update_hotel_price(self, page_id: str, price: float, currency: str = "EUR"):
        """
        Updates the '💶 Price/night starts at' and 'price last updated' properties.
        """
        now = datetime.now().strftime("%Y-%m-%d")
        properties = {
            "💶 Price/night starts at": {
                "number": price
            },
            "price last updated": {
                "date": {
                    "start": now
                }
            }
        }
        await self.notion.pages.update(page_id=page_id, properties=properties)

    def extract_hotel_data(self, hotel_page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts relevant information from a Notion page object.
        """
        props = hotel_page.get("properties", {})

        # Assuming 'Name' is the title property
        name_prop = props.get("Name", {}).get("title", [])
        name = name_prop[0].get("plain_text") if name_prop else "Unknown"

        # Assuming 'URL' is a url property
        url = props.get("URL", {}).get("url")

        # Assuming 'Region' is a select or multi-select property
        region_prop = props.get("Region", {})
        region = ""
        if region_prop.get("type") == "select":
            region = region_prop.get("select", {}).get("name", "")
        elif region_prop.get("type") == "multi_select":
            regions = [r.get("name") for r in region_prop.get("multi_select", [])]
            region = regions[0] if regions else ""

        # Current price for comparison
        current_price = props.get("💶 Price/night starts at", {}).get("number")

        return {
            "id": hotel_page.get("id"),
            "name": name,
            "url": url,
            "region": region,
            "current_price": current_price
        }
