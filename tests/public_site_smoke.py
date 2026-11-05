"""Daily black-box smoke test for the public SSSWET website."""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = os.environ.get("SSSWET_PUBLIC_URL", "https://gudjencio.github.io/SSSWET/")
ARTIFACTS = Path("artifacts")
ARTIFACTS.mkdir(exist_ok=True)
failures, console_errors, page_errors, failed_local_requests = [], [], [], []
checks = {"url": URL, "checked_at": datetime.now(timezone.utc).isoformat()}

def require(condition, message):
    if not condition:
        failures.append(message)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    context = browser.new_context(viewport={"width": 1440, "height": 1000},
                                  service_workers="allow", reduced_motion="reduce")
    page = context.new_page()
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.on("requestfailed", lambda request: failed_local_requests.append(request.url)
            if request.url.startswith("https://gudjencio.github.io/SSSWET/") else None)

    response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
    checks["http_status"] = response.status if response else None
    require(response is not None and response.ok, "Public page did not return a successful HTTP response")
    page.locator("#title").wait_for(state="visible", timeout=20000)
    require(page.locator(".app-shell").is_visible(), "Main application shell is not visible")
    require(page.locator("#technology-grid").is_visible(), "Technology catalogue is not visible")

    language = page.locator("#language")
    language.wait_for(state="visible", timeout=15000)
    option_count = language.locator("option").count()
    checks["language_options"] = option_count
    require(option_count >= 2, f"Language selector has only {option_count} options")
    if option_count >= 2:
        original = language.input_value()
        alternate = language.locator("option").nth(1).get_attribute("value")
        if alternate:
            language.select_option(alternate)
            require(language.input_value() == alternate, "Language selector did not accept a new value")
            language.select_option(original)

    for selector in ("#bot-control-refresh", "#ssswet-report-button"):
        locator = page.locator(selector)
        require(locator.count() == 1 and locator.is_visible(), f"Required control missing or hidden: {selector}")
        if locator.count() == 1 and locator.is_visible():
            locator.click(timeout=8000)
            if selector == "#ssswet-report-button":
                page.keyboard.press("Escape")

    tech = page.locator("#technology-grid button[data-tech]").first
    require(tech.count() == 1 and tech.is_visible(), "No usable technology-card action is visible")
    if tech.count() == 1 and tech.is_visible():
        tech.click(timeout=8000)
        dialog = page.locator("dialog.technology-dialog")
        require(dialog.count() == 1 and dialog.is_visible(), "Technology action did not open its details dialog")
        if dialog.count() == 1 and dialog.is_visible():
            page.keyboard.press("Escape")

    vtt = page.locator("#virtual-time-travel-launch")
    require(vtt.count() == 1 and vtt.is_visible(), "Virtual Time Travel Mapping link is missing or hidden")
    if vtt.count() == 1:
        require("virtual-time-travel.html" in (vtt.get_attribute("href") or ""), "Virtual Time Travel link target changed")

    worker = page.evaluate("""async () => {
      await Promise.race([navigator.serviceWorker.ready, new Promise(resolve => setTimeout(resolve, 12000))]);
      const registration = await navigator.serviceWorker.getRegistration();
      const active = registration && registration.active;
      const response = await fetch('./sw.js', {cache: 'no-store'});
      const source = await response.text();
      return {supported: 'serviceWorker' in navigator,
        controller: Boolean(navigator.serviceWorker.controller), active: Boolean(active),
        scriptURL: active ? active.scriptURL : null,
        hasNetworkFirstFetch: /Always ask the deployed origin first/.test(source),
        workerSourceStatus: response.status};
    }""")
    checks["service_worker"] = worker
    require(worker["supported"], "Service workers are not supported")
    require(worker["active"], "No active service worker controls the public site")
    if os.environ.get("SSSWET_EXPECT_NETWORK_FIRST", "true").lower() == "true":
        require(worker["hasNetworkFirstFetch"], "Deployed worker lacks the expected network-first policy")

    page.reload(wait_until="domcontentloaded", timeout=45000)
    page.locator("#language").wait_for(state="visible", timeout=20000)
    require(page.locator("#technology-grid button[data-tech]").first.is_enabled(),
            "Technology actions are disabled after reload")

    checks["console_errors"] = console_errors[:30]
    checks["uncaught_page_errors"] = page_errors[:30]
    checks["failed_local_requests"] = failed_local_requests[:30]
    require(not page_errors, f"Uncaught JavaScript errors: {page_errors[:5]}")
    require(not failed_local_requests, f"Failed same-origin requests: {failed_local_requests[:5]}")
    page.screenshot(path=str(ARTIFACTS / "public-site.png"), full_page=True)
    browser.close()

checks["failures"] = failures
(ARTIFACTS / "public-site-report.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
print(json.dumps(checks, indent=2))
if failures:
    print("PUBLIC SITE SMOKE TEST FAILED", file=sys.stderr)
    sys.exit(1)
print("PUBLIC SITE SMOKE TEST PASSED")
