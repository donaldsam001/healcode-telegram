import json
import requests
import httpx
import logging
from telegram import Update
from telegram.ext import ContextTypes


USE_MOCK = True
API_BASE_URL = "http://localhost:8000"


def call_healcode_api(code: str):
    # if USE_MOCK:
    #     with open("mock/mock_healcode.json", "r") as f:
    #         return json.load(f)

    # REAL API (later)
    # if code == "cred":
    #     response = requests.get(
    #         # "http://localhost:8000/credentials",
    #         "http://localhost:8000/health",
    #         json={},
    #         timeout=10
    #     )
    #     return response.json()
    if code == "health":
        response = requests.get(
            "http://localhost:8000/health",
            json={},
            timeout=10
        )
        return response.json()
    
# res=call_healcode_api("health")
# print(res)