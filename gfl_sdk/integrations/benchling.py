import requests

class BenchlingAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.benchling.com/v2"

    def get_sequence(self, sequence_id: str) -> dict:
        headers = {"X-API-Key": self.api_key}
        url = f"{self.base_url}/sequences/{sequence_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
