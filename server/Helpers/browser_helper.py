from playwright.async_api import async_playwright

async def launch_browser(user_agent=None, viewport=None):
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
        user_agent=user_agent or "default-user-agent",
        viewport=viewport,
        bypass_csp=True
    )

    await context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
    )

    return p, browser, context