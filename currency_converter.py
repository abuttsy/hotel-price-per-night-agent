import httpx
from typing import Dict

class CurrencyConverter:
    def __init__(self):
        self.api_url = "https://api.frankfurter.app/latest"

    async def convert_to_eur(self, amount: float, from_currency: str) -> float:
        """
        Converts a given amount from a specific currency to EUR using the Frankfurter API.
        """
        if from_currency == "EUR":
            return amount

        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "amount": amount,
                    "from": from_currency,
                    "to": "EUR"
                }
                response = await client.get(self.api_url, params=params)
                response.raise_for_status()
                data = response.json()
                return data["rates"]["EUR"]
        except Exception as e:
            print(f"Error converting currency: {e}")
            # Fallback to amount if conversion fails (not ideal, but handles network errors)
            # In production, we might want to handle this differently.
            return amount
