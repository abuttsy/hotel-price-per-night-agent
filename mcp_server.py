# /// script
# dependencies = [
#   "mcp",
#   "notion-client",
#   "playwright",
#   "playwright-stealth",
#   "python-dotenv",
#   "httpx",
# ]
# ///
import os
import asyncio
from typing import Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from notion_manager import NotionManager
from scraper import HotelScraper
from currency_converter import CurrencyConverter
from email_manager import EmailManager

# Create an MCP server
mcp = FastMCP("HotelPriceAutomation")

@mcp.tool()
async def run_jules_script(hotel_name: Optional[str] = None, hotel_url: Optional[str] = None) -> str:
    """
    Runs the hotel price update automation.

    Args:
        hotel_name: The name of the hotel to update (searches Notion).
        hotel_url: The official website URL of the hotel (searches Notion).

    If both or either are provided, only matching hotels are updated.
    Otherwise, all hotels needing updates are processed.
    """
    load_dotenv()

    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("DATABASE_ID")
    email_sender = os.getenv("EMAIL_SENDER")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_receiver = os.getenv("EMAIL_RECEIVER", "ultimatefamilyhotels@gmail.com")

    if not notion_token or not database_id:
        return "Error: NOTION_TOKEN and DATABASE_ID must be set in environment variables."

    notion_mgr = NotionManager(notion_token, database_id)
    scraper = HotelScraper()
    converter = CurrencyConverter()
    email_mgr = EmailManager(email_sender, email_password, email_receiver)

    results_summary = []
    hotels_to_update = []

    try:
        if hotel_url:
            # Query by URL
            query_filter = {
                "property": "Website",
                "url": {
                    "equals": hotel_url
                }
            }
            response = await notion_mgr.notion.request(
                path=f"databases/{database_id.replace('-', '')}/query",
                method="POST",
                body={"filter": query_filter}
            )
            hotels_to_update = response.get("results", [])
        elif hotel_name:
            # Query by search (best effort)
            response = await notion_mgr.notion.request(
                path="search",
                method="POST",
                body={"query": hotel_name}
            )
            hotels_to_update = [h for h in response.get("results", []) if h.get("object") == "page"]
        else:
            # Update all hotels needing update
            hotels_to_update = await notion_mgr.get_hotels_to_update()

        if not hotels_to_update:
            return "No matching hotels found needing update."

        await scraper.start()

        for hotel_page in hotels_to_update:
            # Skip if it's not a page
            if hotel_page.get("object") != "page":
                continue

            hotel_data = notion_mgr.extract_hotel_data(hotel_page)
            name = hotel_data["name"]
            url = hotel_data["url"]
            region = "Europe" # Default logic
            current_price = hotel_data["current_price"]

            if not url:
                results_summary.append(f"Skipped {name}: No URL found in Notion.")
                continue

            print(f"Processing {name} ({url})...")
            price, currency = await scraper.get_price(url, region)

            if price is not None:
                new_price_eur = await converter.convert_to_eur(price, currency)
                print(f"New price: {new_price_eur:.2f} EUR")
                await notion_mgr.update_hotel_price(hotel_page["id"], new_price_eur)

                if current_price is not None:
                    email_mgr.send_price_alert(name, current_price, new_price_eur)

                results_summary.append(f"Updated {name}: {new_price_eur:.2f} EUR")
            else:
                results_summary.append(f"Failed to scrape {name}")

    except Exception as e:
        import traceback
        return f"An error occurred: {str(e)}\n{traceback.format_exc()}"
    finally:
        await scraper.stop()

    return "\n".join(results_summary) if results_summary else "No updates performed."

if __name__ == "__main__":
    # Check for transport type in environment variable, default to stdio
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "sse":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        # Railway and other PaaS usually provide the port in the PORT environment variable
        port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run(transport="stdio")
