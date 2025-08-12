import asyncio
import random

async def safe_goto(page, url, max_attempts=4, timeout=20000):
    for attempt in range(max_attempts):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            print(f"Successfully navigated to '{url}' after {attempt + 1} attempt(s)")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            await asyncio.sleep(2 + random.uniform(0, 2))
    raise Exception("Failed to navigate after multiple attempts.")