import asyncio
import random

async def safe_goto(page, url, max_attempts=4):
    last_err = None
    for attempt in range(1, max_attempts+1):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return
        except Exception as e1:
            last_err = e1
            try:
                await page.goto(url, wait_until="commit", timeout=20000)
                await page.wait_for_selector("body", state="attached", timeout=10000)
                return
            except Exception as e2:
                last_err = e2
                await asyncio.sleep(min(2 * attempt, 8))
    raise RuntimeError(f"Failed to navigate to {url} after {max_attempts} attempts: {last_err}")