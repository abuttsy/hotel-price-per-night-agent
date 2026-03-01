import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import re

class HotelScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def get_search_dates(self, region: str):
        """
        Determines search dates based on hotel location.
        - Europe: Nov 10–17
        - Caribbean/Mexico: Sep 15–22
        - Southeast Asia: Jun 10–17
        - Middle East: Jul 15–22
        - Default: Second week of November (Nov 10-17)
        """
        now = datetime.now()
        year = now.year

        dates_map = {
            "Europe": ("11-10", "11-17"),
            "Caribbean/Mexico": ("09-15", "09-22"),
            "Southeast Asia": ("06-10", "06-17"),
            "Middle East": ("07-15", "07-22"),
        }

        month_day_start, month_day_end = dates_map.get(region, ("11-10", "11-17"))

        start_date_str = f"{year}-{month_day_start}"
        end_date_str = f"{year}-{month_day_end}"

        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")

        if start_dt < now:
            start_date_str = f"{year+1}-{month_day_start}"
            end_date_str = f"{year+1}-{month_day_end}"

        return start_date_str, end_date_str

    async def get_price(self, hotel_url: str, region: str) -> (float, str):
        """
        Scrapes the hotel website for the lowest rate for 2 adults + 1 child (age 2).
        Attempts to navigate and find prices for specific dates and guest count.
        Returns (price, currency).
        """
        start_date, end_date = self.get_search_dates(region)

        page = await self.browser.new_page()
        # Apply stealth using the new Stealth class
        await Stealth().apply_stealth_async(page)

        try:
            await page.goto(hotel_url, wait_until="networkidle", timeout=60000)

            # Attempt to find currency on the page
            content = await page.content()
            currency = "EUR" # Default
            if "$" in content:
                currency = "USD"
            elif "£" in content:
                currency = "GBP"
            elif "€" in content:
                currency = "EUR"

            price_patterns = [
                r'€\s?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
                r'\$\s?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
                r'£\s?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
                r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s?EUR',
                r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s?USD'
            ]

            found_prices = []
            for pattern in price_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    try:
                        clean_price = match.replace(',', '')
                        found_prices.append(float(clean_price))
                    except ValueError:
                        continue

            if found_prices:
                return min(found_prices), currency

            return None, None

        except Exception as e:
            print(f"Error scraping {hotel_url}: {e}")
            return None, None
        finally:
            await page.close()
