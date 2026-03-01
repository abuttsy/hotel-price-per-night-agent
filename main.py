import os
import asyncio
from dotenv import load_dotenv
from notion_manager import NotionManager
from scraper import HotelScraper
from currency_converter import CurrencyConverter
from email_manager import EmailManager

async def run_automation():
    load_dotenv()

    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("DATABASE_ID")
    email_sender = os.getenv("EMAIL_SENDER")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_receiver = os.getenv("EMAIL_RECEIVER", "ultimatefamilyhotels@gmail.com")

    if not notion_token or not database_id:
        print("Error: NOTION_TOKEN and DATABASE_ID must be set in environment variables.")
        return

    notion_mgr = NotionManager(notion_token, database_id)
    scraper = HotelScraper()
    converter = CurrencyConverter()
    email_mgr = EmailManager(email_sender, email_password, email_receiver)

    print("Fetching hotels to update from Notion...")
    hotels_to_update = await notion_mgr.get_hotels_to_update()
    print(f"Found {len(hotels_to_update)} hotels needing updates.")

    if not hotels_to_update:
        return

    await scraper.start()

    try:
        for hotel_page in hotels_to_update:
            hotel_data = notion_mgr.extract_hotel_data(hotel_page)
            hotel_name = hotel_data["name"]
            hotel_url = hotel_data["url"]
            region = hotel_data["region"]
            current_price_eur = hotel_data["current_price"]

            if not hotel_url:
                print(f"Skipping {hotel_name}: No URL found.")
                continue

            print(f"Scraping price for {hotel_name}...")
            price, currency = await scraper.get_price(hotel_url, region)

            if price is not None:
                print(f"Scraped Price: {price} {currency}")
                new_price_eur = await converter.convert_to_eur(price, currency)
                print(f"Converted Price: {new_price_eur:.2f} EUR")

                print(f"Updating Notion for {hotel_name}...")
                await notion_mgr.update_hotel_price(hotel_data["id"], new_price_eur)

                # Check for price swing and send alert
                if current_price_eur is not None:
                    email_mgr.send_price_alert(hotel_name, current_price_eur, new_price_eur)
                else:
                    print(f"Initial price set for {hotel_name}. No alert sent.")
            else:
                print(f"Could not find price for {hotel_name}.")

    finally:
        await scraper.stop()
        print("Automation complete.")

if __name__ == "__main__":
    asyncio.run(run_automation())
