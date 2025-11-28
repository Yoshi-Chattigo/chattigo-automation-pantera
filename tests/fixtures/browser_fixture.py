import pytest
from playwright.sync_api import sync_playwright
from tests.helpers.config_loader import load_settings

@pytest.fixture(scope="session")
def settings():
    return load_settings()

@pytest.fixture(scope="session")
def pw():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(pw, settings, pytestconfig):
    headed_flag = pytestconfig.getoption("--headed")

    # si el usuario pasa --headed → usamos headed
    headless = not headed_flag if headed_flag is not None else settings.headless

    browser = getattr(pw, settings.browser).launch(headless=headless)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser, settings):
    context = browser.new_context(base_url=settings.base_url)
    page = context.new_page()
    page.set_default_timeout(settings.default_timeout)
    yield page
    context.close()
