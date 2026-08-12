import asyncio
import os
import time
from typing import Any, Awaitable, Callable, Optional

import requests
from dotenv import load_dotenv

try:
    from .auth_token import Database
except ImportError:
    from auth_token import Database


load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
VALIDATION_TTL_SECONDS = 60

ENDPOINTS = {
    "CREDENTIAL": "/api/credential",
    "GIT": "/api/credential/token",
    "ME": "/api/credential/me",
    "REPO": "/api/git/repo",
    "BRANCH": "/api/git/branche",
    "STATUS": "/api/git/status",
    "FIX": "/api/fix",
    "FIX_CANCEL": "/api/fix/cancel",
    "SETUP_REPO": "/api/git/repo",
}

InvalidationCallback = Callable[[int], Optional[Awaitable[None]]]


class HealCodeClient:
    def __init__(self, user_id: int, db: Database, token: Optional[str] = None):
        self.user_id = int(user_id)
        self.db = db
        self.api_auth_token = token
        self.is_valid = bool(token)
        self.last_validated: Optional[float] = None
        self._on_invalid: Optional[InvalidationCallback] = None

    @classmethod
    async def create(cls, user_id: int, db: Database):
        token = await db.get_token(int(user_id))
        return cls(user_id=int(user_id), db=db, token=token)

    def set_invalidation_callback(self, callback: InvalidationCallback):
        self._on_invalid = callback

    async def set_token(self, token: str):
        self.api_auth_token = token
        self.is_valid = bool(token)
        self.last_validated = None
        await self.db.set_token(self.user_id, token)

    async def invalidate(self):
        self.is_valid = False
        self.last_validated = None
        if self._on_invalid:
            maybe_awaitable = self._on_invalid(self.user_id)
            if maybe_awaitable is not None and asyncio.iscoroutine(maybe_awaitable):
                await maybe_awaitable

    async def ensure_valid(self, force: bool = False) -> bool:
        if not self.api_auth_token:
            await self.invalidate()
            return False

        now = time.time()
        if (
            not force
            and self.is_valid
            and self.last_validated is not None
            and (now - self.last_validated) < VALIDATION_TTL_SECONDS
        ):
            return True

        result = await self.get_me(skip_validation=True)
        if isinstance(result, dict) and "error" in result:
            if result.get("status_code") == 401:
                await self.invalidate()
            return False

        self.is_valid = True
        self.last_validated = now
        return True

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        timeout: int = 15,
        skip_validation: bool = False,
    ) -> Any:
        if not skip_validation:
            valid = await self.ensure_valid()
            if not valid:
                return {"error": "Unauthorized", "status_code": 401}

        url = f"{API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {"Content-Type": "application/json"}
        if self.api_auth_token:
            headers["Authorization"] = f"Bearer {self.api_auth_token}"

        try:
            response = await asyncio.to_thread(
                requests.request,
                method,
                url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            return {"error": str(exc)}

        if response.status_code == 401:
            await self.invalidate()
            return {"error": "Unauthorized", "status_code": 401}

        content_type = response.headers.get("Content-Type", "")
        payload: Any
        if "application/json" in content_type:
            try:
                payload = response.json()
            except ValueError:
                payload = {"message": response.text[:300]}
        else:
            payload = {"message": response.text[:300]}

        return self._normalize_api_response(payload, response.status_code)

    def _normalize_api_response(self, payload: Any, http_code: int) -> Any:
        if not isinstance(payload, dict):
            if http_code >= 400:
                return {"error": f"HTTP {http_code}", "status_code": http_code}
            return payload

        if http_code >= 400:
            error_message = payload.get("message") or payload.get("detail") or payload.get("error") or f"HTTP {http_code}"
            return {"error": str(error_message), "status_code": http_code}

        return payload.get("data", payload)

    async def credential_create(self, username: str, provider_id: str = "telegram"):
        return await self._make_request(
            "POST",
            ENDPOINTS["CREDENTIAL"],
            json_data={"provider_id": provider_id, "username": username},
            skip_validation=True,
        )
    
    async def save_git_token(self, token: str):
        return await self._make_request(
            "POST",
            ENDPOINTS["GIT"],
            json_data={"token": token},
            skip_validation=True,
        )
    
    async def get_git_token(self):
        return await self._make_request(
            "GET",
            ENDPOINTS["GIT"],
            skip_validation=True,
        )

    async def get_me(self, skip_validation: bool = False):
        return await self._make_request(
            "GET",
            ENDPOINTS["ME"],
            skip_validation=skip_validation,
        )

    async def get_list_repo(self):
        return await self._make_request("GET", ENDPOINTS["REPO"])

    async def add_repo(self, url: str, branch: str = "main"):
        return await self._make_request(
            "POST",
            ENDPOINTS["REPO"],
            json_data={"url": url, "branch": branch},
        )

    async def switch_branch(self, branch: str):
        return await self._make_request(
            "PUT",
            ENDPOINTS["BRANCH"],
            json_data={"branch": branch},
        )

    async def get_status(self):
        return await self._make_request("GET", ENDPOINTS["STATUS"])

    async def call_fix_api(self, trace_error: str):
        return await self._make_request(
            "POST",
            ENDPOINTS["FIX"],
            json_data={"trace_error": trace_error, "priority": 1},
            timeout=60,
        )

    async def call_cancel_fix(self, request_id: str):
        endpoint = f"{ENDPOINTS['FIX_CANCEL']}/{request_id}"
        return await self._make_request("DELETE", endpoint)

    async def setup_repo(self, repo_url: str, branch: str, chat_id: int):
        """Register a webhook token mapping for the authenticated Telegram user."""
        return await self._make_request(
            "POST",
            ENDPOINTS["SETUP_REPO"],
            json_data={"url": repo_url, "branch": branch},
        )
