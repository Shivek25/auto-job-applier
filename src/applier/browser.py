# src/applier/browser.py
import os
import random
import asyncio
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, BrowserContext, Page
from playwright_stealth import Stealth

class BrowserManager:
    def __init__(
        self,
        headless: bool = False,
        user_data_dir: Optional[str] = None,
        profile_name: str = "Default"
    ):
        self.headless = headless
        # Default to local AppData Chrome User Data if not specified
        default_chrome_dir = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        self.user_data_dir = user_data_dir or default_chrome_dir
        self.profile_name = profile_name
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self._stealth = Stealth()

    async def start(self) -> BrowserContext:
        if self.context:
            return self.context
        self.playwright = await async_playwright().start()
        profile_path = Path(self.user_data_dir) / self.profile_name
        profile_path.mkdir(parents=True, exist_ok=True)
        
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=self.headless,
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars"
            ]
        )
        return self.context

    async def new_stealth_page(self) -> Page:
        if not self.context:
            await self.start()
        page = await self.context.new_page()
        try:
            await self._stealth.apply_stealth_async(page)
        except Exception:
            pass
        return page

    async def random_delay(self, min_sec: float = 1.5, max_sec: float = 4.0):
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    async def human_type(self, element, text: str):
        for char in text:
            await element.type(char, delay=random.randint(40, 110))

    async def close(self):
        if self.context:
            await self.context.close()
            self.context = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
