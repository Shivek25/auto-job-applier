import pytest
import os
from pathlib import Path
from src.applier.browser import BrowserManager

def test_browser_manager_init(tmp_path):
    bm = BrowserManager(
        headless=True,
        user_data_dir=str(tmp_path / "chrome_user_data"),
        profile_name="Profile1"
    )
    assert bm.headless is True
    assert bm.profile_name == "Profile1"
    assert "Profile1" in str(Path(bm.user_data_dir) / bm.profile_name)

@pytest.mark.asyncio
async def test_browser_manager_lifecycle(tmp_path):
    bm = BrowserManager(
        headless=True,
        user_data_dir=str(tmp_path / "chrome_test_profile"),
        profile_name="Test"
    )
    # Test browser launch and stealth page creation
    page = await bm.new_stealth_page()
    assert page is not None
    await page.goto("about:blank")
    title = await page.title()
    assert title == ""
    await page.close()
    await bm.close()
