import time, asyncio, re
from ..celery_app import celery
from ..Helpers.time_tracker import timer
from ..Helpers.safe_goto import safe_goto
from ..Helpers.browser_helper import launch_browser
# from ..Helpers.random_context import get_random_context_params
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
    logger.info(f"Starting scrape_advance for search term: {search} on {url}")
    advance_results = []

    p = browser = context = None
    try:
        try:
            logger.info("Launching Playwright for Advance...")
            p, browser, context = await asyncio.wait_for(
                launch_browser(),
                timeout=30
            )
            logger.info("Playwright launched for Advance")
        except asyncio.TimeoutError:
            logger.warning("Advance Browser launch timed out, retrying...")
            raise

        page = await context.new_page()
        scrape_start = time.time()

        await safe_goto(page, url)
        ele = page.get_by_role("link", name="Shop Here").first
        await ele.wait_for(state="visible", timeout=10000)
        await ele.scroll_into_view_if_needed()

        href = await ele.get_attribute("href")
        await page.goto(href, wait_until="domcontentloaded", timeout=30000)

        STREET_RE = re.compile(r"^\s*\d{1,6}\s+[\w\.\-#'\s]+$", re.I)
        CITY_ST_ZIP_RE = re.compile(r"^[A-Za-z][A-Za-z\s\.\-']+,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?$")

        root = page.locator("main, [role='main'], body").first

        address_container = root.locator("div").filter(
            has=root.locator("div", has_text=STREET_RE)
        ).filter(
            has=root.locator("div", has_text=CITY_ST_ZIP_RE)
        ).first

        await address_container.wait_for(state="visible", timeout=15000)

        street_ele = address_container.locator(":scope div", has_text=STREET_RE).first
        city_ele = address_container.locator(":scope div", has_text=CITY_ST_ZIP_RE).first

        street = (await street_ele.inner_text()).strip()
        city_st_zip = (await city_ele.inner_text()).strip()

        logger.info(f"EXTRACTED ADDRESS: {street} | {city_st_zip}")
        data = {"url": page.url, "title": await page.title(), "store": [street, city_st_zip]}

        await safe_goto(page, f"https://shop.advanceautoparts.com/web/SearchResults?searchTerm={search}")
        await page.wait_for_selector(".css-rps5gr", timeout=60000)
        elements = await page.query_selector_all(".css-13pqr4x")
        listings = []
        for ele in elements:
            img_ele = await ele.query_selector("img")
            name_ele = await ele.query_selector("p[title]")
            price_ele = await ele.query_selector("[aria-label] .css-iib095")
            part_num_ele = await ele.query_selector(".css-scvhiv")
            availability_ele = await ele.query_selector(".css-1tq25me") or await ele.query_selector(".css-ljuqvw")
            link_ele = await ele.query_selector(".css-1my37vd")
            if not price_ele:
                price_ele = await ele.query_selector(".css-iib095")
            
            image = await img_ele.get_attribute("src") if img_ele else None
            name = (await name_ele.text_content()).strip() if name_ele else None
            price = (await price_ele.get_attribute("aria-label") or (await price_ele.text_content()).strip())
            part_number = await part_num_ele.inner_text() if part_num_ele else None
            availability = await availability_ele.inner_text() if availability_ele else None
            link = await link_ele.get_attribute("href") if link_ele else None

            listings.append({"image": image, "name": name, "price": price, "part_number": part_number, "availability": availability, "link": link})

        data["prices"] = listings
        data["total_prices"] = len(data["prices"])
        time_taken = time.time() - scrape_start
        data["time_taken"] = f"{time_taken:.2f}"
        advance_results.append(data)
        print("DATA =====>", data, "<=========== DATA")
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