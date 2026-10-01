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
        if not user_data_dir:
            self.user_data_dir = str(Path("storage/browser_profile").resolve())
        else:
            self.user_data_dir = user_data_dir
        self.profile_name = profile_name
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self._stealth = Stealth()

    async def start(self) -> BrowserContext:
        if self.context:
            return self.context
        self.playwright = await async_playwright().start()
        profile_path = Path(self.user_data_dir)
        profile_path.mkdir(parents=True, exist_ok=True)
        
        launch_kwargs = {
            "user_data_dir": str(profile_path),
            "headless": self.headless,
            "viewport": {"width": 1280, "height": 800},
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars"
            ]
        }
        try:
            # Try launching with real Chrome channel installed on system
            self.context = await self.playwright.chromium.launch_persistent_context(
                channel="chrome",
                **launch_kwargs
            )
        except Exception:
            # Fallback to standard Playwright Chromium
            self.context = await self.playwright.chromium.launch_persistent_context(
                **launch_kwargs
            )
        return self.context

    async def login_wizard(self, platform: str = "linkedin"):
        self.headless = False
        page = await self.new_stealth_page()
        if platform == "linkedin":
            target_url = "https://www.linkedin.com/login"
        elif platform == "indeed":
            target_url = "https://secure.indeed.com/auth"
        else:
            target_url = "https://www.google.com"

        await page.goto(target_url)
        print(f"\n{'='*65}")
        print(f"🔑 Please sign in to {platform.title()} in the opened Chrome browser window.")
        print(f"👉 Once you are logged in, press [Enter] here in the console to save your session.")
        print(f"{'='*65}\n")
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, input)
        print(f"✅ Session and cookies saved permanently to {self.user_data_dir}!")
        await page.close()

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
