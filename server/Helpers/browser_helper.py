import os
from playwright.async_api import async_playwright

ua = os.getenv(
    "AUTO_PARTS_BROWSER_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)

async def launch_browser():
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True, args=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-quic",
        "--disable-blink-features=AutomationControlled",
        '--disable-infobars',
        "--disable-http2",
    ])

    context = await browser.new_context(
        user_agent=ua,
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        timezone_id="America/Denver",
        ignore_https_errors=True,
    )

    await context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
    )

    return p, browser, context