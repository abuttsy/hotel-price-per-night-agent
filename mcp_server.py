# /// script
# dependencies = [
#   "mcp",
#   "notion-client",
#   "playwright",
#   "playwright-stealth",
#   "python-dotenv",
#   "httpx",
#   "starlette",
#   "uvicorn",
# ]
# ///
import os
import asyncio
import re
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from notion_manager import NotionManager
from scraper import HotelScraper
from currency_converter import CurrencyConverter
from email_manager import EmailManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Logging Middleware to debug headers
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        host = request.headers.get("host")
        logger.info(f"Request: {request.method} {request.url.path} - Host: {host}")
        return await call_next(request)

# Create an MCP server
mcp = FastMCP("HotelPriceAutomation")

@mcp.tool()
async def run_jules_script(hotel_name: Optional[str] = None, hotel_url: Optional[str] = None) -> str:
    """
    Runs the hotel price update automation.

    Args:
        hotel_name: The name of the hotel to update (searches Notion).
        hotel_url: The Notion page URL (database row URL) of the hotel.

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
            # Extract page ID from Notion URL if possible
            match = re.search(r'([a-f0-9]{32})', hotel_url)
            if match:
                page_id = match.group(1)
                try:
                    response = await notion_mgr.notion.request(
                        path=f"pages/{page_id}",
                        method="GET"
                    )
                    hotels_to_update = [response]
                except Exception as e:
                    return f"Error fetching Notion page from URL: {str(e)}"
            else:
                return f"Could not extract a valid page ID from the provided hotel_url: {hotel_url}"
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
            if hotel_page.get("object") != "page":
                continue

            hotel_data = notion_mgr.extract_hotel_data(hotel_page)
            name = hotel_data["name"]
            website = hotel_data["url"]
            region = "Europe" # Default logic
            current_price = hotel_data["current_price"]

            if not website:
                results_summary.append(f"Skipped {name}: No official website URL found in Notion.")
                continue

            logger.info(f"Processing {name} ({website})...")
            price, currency = await scraper.get_price(website, region)

            if price is not None:
                new_price_eur = await converter.convert_to_eur(price, currency)
                logger.info(f"New price: {new_price_eur:.2f} EUR")
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
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "sse":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8080")))

        starlette_app = mcp.sse_app
        if callable(starlette_app):
            starlette_app = starlette_app()

        # Add middlewares
        starlette_app.add_middleware(LoggingMiddleware)
        # Allow all hosts to avoid 421/400 errors
        starlette_app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

        logger.info(f"Starting SSE server on {host}:{port}")
        uvicorn.run(starlette_app, host=host, port=port)
    else:
        mcp.run(transport="stdio")
