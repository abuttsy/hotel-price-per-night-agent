import os
import asyncio
from dotenv import load_dotenv
from notion_manager import NotionManager
from scraper import HotelScraper
from currency_converter import CurrencyConverter
from email_manager import EmailManager

async def run_quellenhof():
    load_dotenv()

    notion_token = os.getenv("NOTION_TOKEN")
    database_id = "58f6e6a92c684fe99100e9808b4e7e31"
    email_sender = os.getenv("EMAIL_SENDER")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_receiver = os.getenv("EMAIL_RECEIVER", "ultimatefamilyhotels@gmail.com")

    notion_mgr = NotionManager(notion_token, database_id)
    scraper = HotelScraper()
    converter = CurrencyConverter()
    email_mgr = EmailManager(email_sender, email_password, email_receiver)

    # Manual search for Quellenhof page
    response = await notion_mgr.notion.request(
        path="search",
        method="POST",
        body={"query": "Quellenhof"}
    )
    results = response.get("results", [])
    if not results:
        print("Quellenhof not found.")
        return

    hotel_page = results[0]
    hotel_data = notion_mgr.extract_hotel_data(hotel_page)
    hotel_name = hotel_data["name"]
    hotel_url = hotel_data["url"]
    region = "Europe" # Hardcoded for test
    current_price_eur = hotel_data["current_price"]

    print(f"Testing {hotel_name} with URL {hotel_url}...")

    await scraper.start()

    try:
        price, currency = await scraper.get_price(hotel_url, region)

        if price is not None:
            print(f"Scraped Price: {price} {currency}")
            new_price_eur = await converter.convert_to_eur(price, currency)
            print(f"Converted Price: {new_price_eur:.2f} EUR")

            print(f"Updating Notion for {hotel_name}...")
            await notion_mgr.update_hotel_price(hotel_data["id"], new_price_eur)

            if current_price_eur is not None:
                email_mgr.send_price_alert(hotel_name, current_price_eur, new_price_eur)
            else:
                print(f"Initial price set for {hotel_name}.")
        else:
            print(f"Could not find price for {hotel_name}.")

    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(run_quellenhof())
