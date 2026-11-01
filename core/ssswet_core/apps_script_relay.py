"""Optional success-only notification relay for the SSSWET Apps Script endpoint."""
from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class AppsScriptSuccessRelay:
    """Send one compact notification per completed research cycle."""

    def __init__(self, endpoint: str = "", secret: str = "", timeout: float = 15.0):
        self.endpoint = (endpoint or os.environ.get("SSSWET_RELAY_URL", "")).strip()
        self.secret = (secret or os.environ.get("SSSWET_RELAY_SECRET", "")).strip()
        self.timeout = max(3.0, min(float(timeout), 30.0))

    @property
    def configured(self) -> bool:
        return bool(self.endpoint and self.secret)

    def send_cycle_success(self, completed: list[dict]) -> bool:
        if not self.configured or not completed:
            return False
        if not self.endpoint.startswith("https://"):
            raise ValueError("SSSWET_RELAY_URL must use HTTPS.")
        # Keep notifications compact: no raw agent deliberations or personal data.
        safe_items = []
        for item in completed:
            safe_items.append({
                "technology": str(item.get("technology", ""))[:100],
                "task_id": str(item.get("task_id", ""))[:100],
                "passes": int(item.get("passes", 0)),
                "evidence_count": int(item.get("evidence_count", 0)),
                "summary": str(item.get("summary", ""))[:500],
            })
        payload = {
            "secret": self.secret,
            "type": "research_success",
            "technology": "SSSWET research cycle",
            "summary": "Completed successfully: " + ", ".join(item["technology"] for item in safe_items) + ".",
            "completed": safe_items,
            "success_count": len(safe_items),
        }
        request = Request(
            self.endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read(4096).decode("utf-8", errors="replace")
                if response.status < 200 or response.status >= 300:
                    raise RuntimeError(f"Apps Script relay returned HTTP {response.status}.")
                print(f"[SSSWET] Success notification accepted by Apps Script ({response.status}).")
                return True
        except HTTPError as exc:
            detail = exc.read(1000).decode("utf-8", errors="replace")
            raise RuntimeError(f"Apps Script relay rejected notification (HTTP {exc.code}): {detail}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"Apps Script relay unavailable: {type(exc).__name__}") from exc
