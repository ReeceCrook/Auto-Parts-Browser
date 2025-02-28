from playwright.async_api import async_playwright

async def launch_browser(user_agent=None, viewport=None):
    p = await async_playwright().start()
    browser = await p.firefox.launch(
        headless=True,
        args=[
            '--disable-gpu',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--disable-features=HTTP2'
        ]
        )
    context = await browser.new_context(
        user_agent=user_agent or "default-user-agent",
        viewport=viewport,
        bypass_csp=True
    )
    return browser, context