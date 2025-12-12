from playwright.sync_api import Page, Locator
from utils.logger import get_logger

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

    def navigate(self, url: str):
        self.logger.info(f"Navigating to {url}")
        self.page.goto(url)

    def click(self, selector: str, **kwargs):
        self.logger.info(f"Clicking element: {selector}")
        self.page.click(selector, **kwargs)

    def fill(self, selector: str, text: str):
        self.logger.info(f"Filling element {selector} with text: {text}")
        self.page.fill(selector, text)

    def get_text(self, selector: str) -> str:
        self.logger.info(f"Getting text from element: {selector}")
        return self.page.inner_text(selector)

    def is_visible(self, selector: str) -> bool:
        self.logger.info(f"Checking visibility of element: {selector}")
        return self.page.is_visible(selector)
