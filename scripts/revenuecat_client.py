"""Simple RevenueCat API helper."""
import os
import requests


class RevenueCatClient:
    """Wrapper for RevenueCat REST API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get('REVENUECAT_API_KEY', '')
        self.base_url = 'https://api.revenuecat.com/v1'
        if not self.api_key:
            raise ValueError('RevenueCat API key not provided')

    def _headers(self) -> dict:
        return {'Authorization': f'Bearer {self.api_key}'}

    def get_customer_info(self, app_user_id: str) -> dict:
        resp = requests.get(f'{self.base_url}/subscribers/{app_user_id}', headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def create_purchase(self, app_user_id: str, product_id: str) -> dict:
        payload = {'app_user_id': app_user_id, 'product_id': product_id}
        resp = requests.post(f'{self.base_url}/receipts', json=payload, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()
