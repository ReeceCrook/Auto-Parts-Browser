import time
import asyncio
from ..celery_app import celery
from ..Helpers.time_tracker import timer
from ..Helpers.safe_goto import safe_goto
from ..Helpers.browser_helper import launch_browser
from ..Helpers.random_context import get_random_context_params

@celery.task(name="tasks.scrape_oreilly")
@timer
def scrape_oreilly(search):
    return asyncio.run(async_scrape_oreilly(search))

async def async_scrape_oreilly(search):
    url = f"https://www.oreillyauto.com/search?q={search}"
    oreilly_results = []
    browser = None
    try:
        user_agent, viewport = get_random_context_params()
        browser, context = await launch_browser(user_agent=user_agent, viewport=viewport)
        page = await context.new_page()
            
        scrape_start = time.time()
        await safe_goto(page, url)
        data = {"url": url, "title": await page.title()}

        await page.wait_for_selector(".pricing_price", timeout=60000)
                            
        # The below section of code is needed due to oreillyauto's lazy loading
        prev_count = 0
        while True:
            elements = await page.query_selector_all(".pricing_price")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(500)
            count = len(elements)
            if count == prev_count:
                break
            prev_count = count
            
        time_taken = time.time() - scrape_start
        data["prices"] = [await element.inner_text() for element in elements]
        data["total_prices"] = len(data["prices"])
        data["time_taken"] = f"{time_taken:.2f}"
        oreilly_results.append(data)
    finally:
        if browser:
            await browser.close()

    return oreilly_results
