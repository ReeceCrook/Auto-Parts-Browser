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
from billiard.exceptions import TimeLimitExceeded

logger = get_task_logger(__name__)
@celery.task(
    name="tasks.scrape_oreilly",
    queue="oreilly",
    soft_time_limit=180,
    time_limit=240,
    acks_late=True,
    bind=True,
    autoretry_for=(SoftTimeLimitExceeded, TimeLimitExceeded, Exception),
    retry_backoff=True,
    retry_kwargs={'max_retries': 5},
)
def scrape_oreilly(self, search, url):
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(async_scrape_oreilly(search, url))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
    return result

def extract_store_id(url):
    match = re.search(r'autoparts-(\d+)\.html', url)
    if match:
        print(match)
        return match.group(1)
    return None

async def async_scrape_oreilly(search, url):
    logger.info(f"Starting scrape_oreilly for search term: {search} on {url}")
    oreilly_results = []

    p = browser = context = None
    try:
        user_agent, viewport = get_random_context_params()
        try:
            logger.info("Launching Playwright for Oreilly...")
            p, browser, context = await asyncio.wait_for(
                launch_browser(user_agent=user_agent, viewport=viewport),
                timeout=30
            )
            logger.info("Playwright launched for Oreilly")
        except asyncio.TimeoutError:
            logger.warning("Oreilly Browser launch timed out, retrying...")
            raise
                
        page = await context.new_page()
            
        scrape_start = time.time()
        store_id = extract_store_id(url)
        logger.info(f"Store ID ==> {store_id}")
        
        await safe_goto(page, url)
        ele = await page.wait_for_selector(f'a.js-shop-now[data-store-id="{store_id}"]', timeout=60000)
        await ele.click(timeout=60000)
        await safe_goto(page, f"https://www.oreillyauto.com/search?q={search}")

        await page.wait_for_selector(
            "small.header-navigation-label__label__subtitle:has-text('Selected Store') + span.header-navigation-label__label__text",
            state="visible", timeout=15000
        )
        location_text = (await page.text_content(
            "small.header-navigation-label__label__subtitle:has-text('Selected Store') + span.header-navigation-label__label__text"
        )).strip()

        logger.info(f"LOCATION ===> {location_text} <===")

        data = {"url": url, "title": await page.title(), "store": location_text}
        print(data)

        await page.wait_for_selector('article.product.product--plp.product--interchange.js-product[role="article"]', timeout=120000)
        
        # The below section of code is needed due to oreillyauto's lazy loading                    
        prev_count = 0
        while True:
            elements = await page.query_selector_all('article.product.product--plp.product--interchange.js-product[role="article"]')
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(100)
            count = len(elements)
            if count == prev_count:
                break
            prev_count = count
            
        time_taken = time.time() - scrape_start
        
        listings = []
        for ele in elements:
            img_ele = await ele.query_selector("img")
            name_ele = await ele.query_selector(".product__name")
            price_ele = await ele.query_selector(".product-pricing__price")
            part_num_ele = await ele.query_selector(".part-info")
            availability_ele = await ele.query_selector(".pickup-eligibility-status")
            link_ele = await ele.query_selector(".product__link")

            image = await img_ele.get_attribute("src") if img_ele else None
            name = (await name_ele.text_content()).strip() if name_ele else None
            price = await price_ele.inner_text() if price_ele else None
            part_number = await part_num_ele.inner_text() if part_num_ele else None
            availability = await availability_ele.inner_text() if availability_ele else None
            link = await link_ele.get_attribute("href") if link_ele else None

            listings.append({"image": image, "name": name, "price": price, "part_number": part_number, "availability": availability, "link": link})

        data["prices"] = listings
        data["total_prices"] = len(data["prices"])
        data["time_taken"] = f"{time_taken:.2f}"
        oreilly_results.append(data)
        logger.info(f"Completed scrape_oreilly for search term: {search} in {time_taken:.2f} sec on {url}")

    except Exception:
        logger.exception(f"Error in oreilly_scraper for {search!r} @ {url!r}")
        raise
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if p:
            await p.stop()


    return oreilly_results
