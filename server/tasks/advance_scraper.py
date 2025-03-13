import time
import asyncio
from ..celery_app import celery
from ..Helpers.time_tracker import timer
from ..Helpers.safe_goto import safe_goto
from ..Helpers.browser_helper import launch_browser
from ..Helpers.random_context import get_random_context_params
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
@celery.task(name="tasks.scrape_advance", soft_time_limit=300, time_limit=310, acks_late=True)
#@timer
def scrape_advance(search):
    return asyncio.run(async_scrape_advance(search))

async def async_scrape_advance(search):
    logger.info(f"Starting scrape_advance for search term: {search}")
    url = "https://stores.advanceautoparts.com/co/centennial/6701-s-potomac-st?utm_medium=local&utm_source=yext&utm_content=listing-2018-03-22&utm_campaign=aap"
    advance_results = []
    user_agent, viewport = get_random_context_params()
    browser, context = await launch_browser(user_agent=user_agent, viewport=viewport)
    try:
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
        logger.info(f"Completed scrape_advance for search term: {search} in {time_taken:.2f} sec")
    except Exception as e:
        logger.error(f"Error in scrape_advance for search '{search}': {e}")
        raise
    finally:
        await browser.close()
    return advance_results
