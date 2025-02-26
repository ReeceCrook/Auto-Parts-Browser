import time
from playwright.sync_api import sync_playwright
from celery_app import celery
from time_tracker import timer


@timer
def scrape_links(search):
    
    links = [f"https://www.oreillyauto.com/search?q={search}", f"https://shop.advanceautoparts.com/web/SearchResults?searchTerm={search}"]

    results = []
    with sync_playwright() as p:


        browser = p.firefox.launch(
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
        
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                        "AppleWebKit/537.36 (KHTML, like Gecko) " \
                        "Chrome/98.0.4758.102 Safari/537.36"
        context = browser.new_context(user_agent=user_agent, bypass_csp=True)
        page = context.new_page()
        
        def safe_goto(page, url):
                for attempt in range(3):
                    try:
                        page.goto(url, wait_until="load", timeout=10000)
                        return
                    except Exception as e:
                        print(f"Attempt {attempt + 1} failed: {e}")
                        time.sleep(2)
                raise Exception("Failed to navigate after multiple attempts.")
        
        for link in links:

            safe_goto(page, link)

            data = {"url": link, "title": page.title()}
            page.screenshot(path="home.png")
            
            # oreillyauto and advanced auto parts will be the only supported sites for the beginning stages of this project
            if "oreillyauto" in link:
                page.wait_for_selector(".pricing_price", timeout=60000)
                
                #The below section of code is needed due to oreillyauto's lazy loading

                prev_count = 0
                while True:
                    elements = page.query_selector_all(".pricing_price")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(500)
                    #Only getting prices until I get the basic project setup done, will be the whole listing
                    count = len(elements)
                    if count == prev_count:
                        break
                    prev_count = count

                data["prices"] = [element.inner_text() for element in elements]
                data["total_prices"] = len(data["prices"])
            else:
                #Only getting prices until I get the basic project setup done, will be the whole listing
                page.wait_for_selector(".css-iib095", timeout=60000)
                elements = page.query_selector_all(".css-iib095")
                data["prices"] = [element.get_attribute("aria-label") for element in elements]
                data["total_prices"] = len(data["prices"])
            results.append(data)
        browser.close()
    return results



@celery.task(name="tasks.run_scrape")
def run_scrape(search):
    """
    Celery task to run the playwright scrape.
    """
    result = scrape_links(search)
    return result