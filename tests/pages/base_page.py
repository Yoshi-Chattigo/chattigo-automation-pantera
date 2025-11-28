class BasePage:
    def __init__(self, page):
        self.page = page
        self.base_url = getattr(page.context, "base_url", "").rstrip("/")

    # ========== Navegación ==========
    def goto(self, path: str):
        if path.startswith("http"):
            self.page.goto(path)
        else:
            self.page.goto(f"{self.base_url}{path}")

    # ========== Acciones ==========
    def click(self, selector: str):
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str):
        self.page.locator(selector).fill(value)

    def type(self, selector: str, value: str):
        self.page.locator(selector).type(value)

    # ========== Esperas ==========
    def wait_for_selector(self, selector: str, timeout: int = 5000):
        return self.page.wait_for_selector(selector, timeout=timeout)

    # ========== Utilidades ==========
    def visible(self, selector: str, timeout=5000) -> bool:
        try:
            return self.page.locator(selector).is_visible(timeout=timeout)
        except:
            return False

    def get_text(self, selector: str):
        return self.page.locator(selector).inner_text()
