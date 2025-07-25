import time
import random
import asyncio
from ..celery_app import celery
from ..Helpers.time_tracker import timer
from ..Helpers.safe_goto import safe_goto
from ..Helpers.browser_helper import launch_browser
from ..Helpers.random_context import get_random_context_params
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
from billiard.exceptions import TimeLimitExceeded

logger = get_task_logger(__name__)
@celery.task(
    name="tasks.scrape_advance",
    queue="advance",
    soft_time_limit=90,
    time_limit=120,
    acks_late=True,
    bind=True,
    autoretry_for=(SoftTimeLimitExceeded, TimeLimitExceeded, Exception),
    retry_backoff=True,
    retry_kwargs={'max_retries': 5},
)

def scrape_advance(self, search, url):  
    loop = asyncio.new_event_loop()
    try:
        result= loop.run_until_complete(async_scrape_advance(search, url))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
    return result

async def async_scrape_advance(search, url):
    await asyncio.sleep(random.uniform(1, 3))
    logger.info(f"Starting scrape_advance for search term: {search} on {url}")
    advance_results = []

    p = browser = context = None
    try:
        user_agent, viewport = get_random_context_params()
        try:
            logger.info("Launching Playwright for Advance...")
            p, browser, context = await asyncio.wait_for(
                launch_browser(user_agent=user_agent, viewport=viewport),
                timeout=30
            )
            logger.info("Playwright launched for Advance")
        except asyncio.TimeoutError:
            logger.warning("Advance Browser launch timed out, retrying...")
            raise

        page = await context.new_page()
        scrape_start = time.time()

        await safe_goto(page, url)
        ele = await page.wait_for_selector('a.Button--primary[href*="shop.advanceautoparts.com"]', timeout=60000)
        await ele.click(timeout=60000)
        await page.wait_for_selector('.css-l3rx45', timeout=60000)
        store_elements = await page.query_selector_all('.css-l3rx45')
        store = [await element.inner_text() for element in store_elements]
        data = {"url": url, "title": await page.title(), "store": store}

        await safe_goto(page, f"https://shop.advanceautoparts.com/web/SearchResults?searchTerm={search}")
        await page.wait_for_selector(".css-rps5gr", timeout=60000)
        elements = await page.query_selector_all(".css-13pqr4x")
        data["prices"] = [await element.evaluate("el => el.outerHTML") for element in elements]
        data["total_prices"] = len(data["prices"])
        time_taken = time.time() - scrape_start
        data["time_taken"] = f"{time_taken:.2f}"
        advance_results.append(data)
        logger.info(f"Completed scrape_advance for search term: {search} in {time_taken:.2f} sec on {url}")
    except Exception:
        logger.exception(f"Error in advance_scraper for {search!r} @ {url!r}")
        raise
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if p:
            await p.stop()

    return advance_results