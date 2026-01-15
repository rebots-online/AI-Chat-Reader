# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
"""Simple Gumroad API helper."""
import os
import requests


class GumroadClient:
    """Minimal wrapper for Gumroad's licensing API."""

    def __init__(self, access_token: str | None = None):
        self.access_token = access_token or os.environ.get("GUMROAD_ACCESS_TOKEN", "")
        self.base_url = "https://api.gumroad.com/v2"

    def verify_license(self, product_permalink: str, license_key: str, increment: bool = True) -> dict:
        """Verify a Gumroad license key."""
        data = {
            "product_permalink": product_permalink,
            "license_key": license_key,
            "increment_uses_count": "true" if increment else "false",
        }
        resp = requests.post(f"{self.base_url}/licenses/verify", data=data, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_sale(self, sale_id: str) -> dict:
        """Retrieve sale info (requires vendor access token)."""
        if not self.access_token:
            raise ValueError("Gumroad access token required for sale lookup")
        resp = requests.get(
            f"{self.base_url}/sales/{sale_id}",
            params={"access_token": self.access_token},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
