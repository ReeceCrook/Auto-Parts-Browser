import re
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

logger = get_task_logger(__name__)
@celery.task(
    name="tasks.scrape_oreilly",
    queue="oreilly",
    soft_time_limit=90,
    time_limit=120,
    acks_late=True,
    bind=True,
    autoretry_for=(SoftTimeLimitExceeded,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3, 'countdown': 3},
)
def scrape_oreilly(self, search, url):
    return asyncio.run(async_scrape_oreilly(search, url))

def extract_store_id(url):
    match = re.search(r'autoparts-(\d+)\.html', url)
    if match:
        print(match)
        return match.group(1)
    return None

async def async_scrape_oreilly(search, url):
    await asyncio.sleep(random.uniform(1, 3))
    logger.info(f"Starting scrape_oreilly for search term: {search} on {url}")
    oreilly_results = []
    browser = None
    try:
        user_agent, viewport = get_random_context_params()
        p, browser, context = await launch_browser(user_agent=user_agent, viewport=viewport)
        page = await context.new_page()
            
        scrape_start = time.time()
        store_id = extract_store_id(url)
        logger.info(f"Store ID ==> {store_id}")
        
        await safe_goto(page, url)
        await asyncio.sleep(5)
        ele = await page.wait_for_selector(f'a.js-shop-now[data-store-id="{store_id}"]', timeout=60000)
        await ele.click(timeout=60000)
        await asyncio.sleep(5)
        await safe_goto(page, f"https://www.oreillyauto.com/search?q={search}")
        await asyncio.sleep(5)
        selector = (
            'span.header-icon-button-text--desktop:has(span.header-icon-button-text__top small:has-text("Selected Store")) '
            'span.header-icon-button-text__bottom strong span'
        )
        await page.wait_for_selector(selector, timeout=60000)
        location_element = await page.query_selector(selector)
        location_text = (await location_element.inner_text()).strip()
        logger.info(f"LOCATION TEXT ===> {location_text} <===")

        
        data = {"url": url, "title": await page.title(), "store": location_text}
        print(data)

        await page.wait_for_selector('article.product.product--plp.product--interchange.js-product[role="article"]', timeout=120000)
        
        # The below section of code is needed due to oreillyauto's lazy loading                    
        prev_count = 0
        while True:
            elements = await page.query_selector_all('article.product.product--plp.product--interchange.js-product[role="article"]')
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(500)
            count = len(elements)
            if count == prev_count:
                break
            prev_count = count
            
        time_taken = time.time() - scrape_start
        data["prices"] = [await element.evaluate("el => el.outerHTML") for element in elements]
        data["total_prices"] = len(data["prices"])
        data["time_taken"] = f"{time_taken:.2f}"
        oreilly_results.append(data)
        logger.info(f"Completed scrape_oreilly for search term: {search} in {time_taken:.2f} sec on {url}")
    except Exception as e:
        logger.error(f"Error in scrape_oreilly for search '{search}': {e}")
        raise
    finally:
        if browser:
            await browser.close()
        if p:
            await p.stop()

    return oreilly_results
