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
        Fetches hotels that either have no 'Price last updated' or were updated more than 365 days ago.
        """
        hotels = []
        has_more = True
        start_cursor = None

        one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        query_filter = {
            "or": [
                {
                    "property": "Price last updated",
                    "date": {
                        "is_empty": True
                    }
                },
                {
                    "property": "Price last updated",
                    "date": {
                        "before": one_year_ago
                    }
                }
            ]
        }

        while has_more:
            response = await self.notion.request(
                path=f"databases/{self.database_id.replace('-', '')}/query",
                method="POST",
                body={
                    "filter": query_filter,
                    "start_cursor": start_cursor
                } if start_cursor else {"filter": query_filter}
            )
            hotels.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return hotels

    async def update_hotel_price(self, page_id: str, price: float, currency: str = "EUR"):
        """
        Updates the '💶 Price/night starts at' and 'Price last updated' properties.
        """
        now = datetime.now().strftime("%Y-%m-%d")
        properties = {
            "💶 Price/night starts at": {
                "number": price
            },
            "Price last updated": {
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

        # '🏨 Hotel Name' is the title property
        name_prop = props.get("🏨 Hotel Name", {}).get("title", [])
        name = name_prop[0].get("plain_text") if name_prop else "Unknown"

        # 'Website' is the url property
        url = props.get("Website", {}).get("url")

        # Region extraction (relation or rollup might be complex, default to "" for now)
        region = ""

        # Current price for comparison
        current_price = props.get("💶 Price/night starts at", {}).get("number")

        return {
            "id": hotel_page.get("id"),
            "name": name,
            "url": url,
            "region": region,
            "current_price": current_price
        }
