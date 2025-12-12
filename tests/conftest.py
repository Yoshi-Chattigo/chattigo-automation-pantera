import pytest
from playwright.sync_api import sync_playwright
from config.config import Config
from pages.login_page import LoginPage
import os

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="pantera", help="Environment to run tests against: pantera, bugs, support-bugs, leones")

@pytest.fixture(scope="session", autouse=True)
def configure_env(request):
    env = request.config.getoption("--env")
    if env in Config.ENVIRONMENTS:
        Config.BASE_URL = Config.ENVIRONMENTS[env]
    else:
        # Fallback or custom URL handling if needed
        pass

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=Config.HEADLESS)
        context = browser.new_context(viewport={"width": 1200, "height": 720}, locale="es-ES")
        yield context
        browser.close()

@pytest.fixture(scope="function")
def page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()

@pytest.fixture(scope="function")
def login_page(page):
    return LoginPage(page)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        page = item.funcargs.get("page")
        if page:
            # Create a safe filename from nodeid
            safe_name = item.nodeid.replace("::", "_").replace("/", "_").replace(".py", "")
            screenshot_path = f"screenshots/{safe_name}.png"
            os.makedirs("screenshots", exist_ok=True)
            try:
                page.screenshot(path=screenshot_path)
            except Exception as e:
                print(f"Failed to take screenshot: {e}")
