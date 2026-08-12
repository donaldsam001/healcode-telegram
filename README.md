# healcode-telegram

Telegram entry point for HealCode. The bot preserves its existing Git and manual
`/fix` commands and adds an asynchronous error-reporting setup flow.

## Automatic error fixes

1. Run `/start` in the target Telegram chat. The bot stores both the Telegram
   account id and the **chat id** used for future notifications.
2. Run `/setup_repo https://github.com/org/repo main`.
3. Copy the one-time `heal_…` token to the developer application's environment.
4. Send errors to the HealCode service:

```python
import os
import requests

def report_error(trace_error: str) -> None:
    try:
        requests.post(
            os.getenv("HEALCODE_WEBHOOK_URL", "http://localhost:8000/api/webhook/error"),
            headers={"Authorization": f"Bearer {os.environ['HEALCODE_TOKEN']}"},
            json={"trace_error": trace_error},
            timeout=2,
        )
    except requests.RequestException:
        # Reporting must never take down the developer application.
        pass
```

The token is shown only at setup time. Do not paste it into source control or
Telegram groups where untrusted members can read it.
