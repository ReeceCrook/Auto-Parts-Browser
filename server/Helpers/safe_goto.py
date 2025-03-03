import asyncio

async def safe_goto(page, url):
    for attempt in range(4):
        try:
            await page.goto(url, wait_until="load", timeout=10000)
            print(f"Successfully navigated to '{url}' after {attempt + 1} attempt(s)")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2)
    raise Exception("Failed to navigate after multiple attempts.")
