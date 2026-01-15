# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
"""Basic wrapper for the Alby Lightning API."""
import os
import requests


class AlbyClient:
    """Interact with Alby's Lightning API for pay-as-you-go options."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("ALBY_API_KEY", "")
        self.base_url = "https://api.getalby.com"
        if not self.api_key:
            raise ValueError("Alby API key not provided")

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def create_invoice(self, amount_sats: int, memo: str) -> dict:
        """Create a Lightning invoice."""
        payload = {"amount": amount_sats, "memo": memo}
        resp = requests.post(f"{self.base_url}/invoices", json=payload, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_invoice(self, payment_hash: str) -> dict:
        """Check invoice status."""
        resp = requests.get(f"{self.base_url}/invoices/{payment_hash}", headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()
