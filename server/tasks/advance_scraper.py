import time
import asyncio
from ..celery_app import celery
from ..Helpers.time_tracker import timer
from ..Helpers.safe_goto import safe_goto
from ..Helpers.browser_helper import launch_browser
from ..Helpers.random_context import get_random_context_params


@celery.task(name="tasks.scrape_advance")
@timer
def scrape_advance(search):
    return asyncio.run(async_scrape_advance(search))

async def async_scrape_advance(search):
    advance_results = []
    user_agent, viewport = get_random_context_params()
    browser, context = await launch_browser(user_agent=user_agent, viewport=viewport)
    try:
        page = await context.new_page()
        url = f"https://shop.advanceautoparts.com/web/SearchResults?searchTerm={search}"
        data = {"url": url, "title": await page.title()}
        scrape_start = time.time()
        await safe_goto(page, url)

        await page.wait_for_selector(".css-iib095", timeout=60000)
        elements = await page.query_selector_all(".css-iib095")
        data["prices"] = [await element.get_attribute("aria-label") for element in elements]
        data["total_prices"] = len(data["prices"])
        time_taken = time.time() - scrape_start
        data["time_taken"] = f"{time_taken:.2f}"
        advance_results.append(data)
    finally:
        await browser.close()
    return advance_results
