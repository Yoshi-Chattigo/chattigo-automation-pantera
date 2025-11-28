import pytest
import os
import pathlib


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="pantera")
    parser.addoption("--profile", action="store", default="agente")


@pytest.fixture(scope="session")
def settings(pytestconfig):
    env = pytestconfig.getoption("--env")
    profile = pytestconfig.getoption("--profile")

    os.environ["ENVIRONMENT"] = env
    os.environ["PROFILE"] = profile

    from tests.helpers.config_loader import load_settings
    return load_settings()


# ============================================================
# 🔎 Detectar Cloud Run automáticamente
# ============================================================
def is_cloud_run():
    return (
        os.getenv("K_SERVICE") is not None or
        os.getenv("K_REVISION") is not None or
        pathlib.Path("/.dockerenv").exists()
    )


# ============================================================
# 📌 Fixture page con HEADLESS inteligente
# ============================================================
@pytest.fixture
def page(playwright, settings):
    print("CONFTEXT CARGADO OK — BASE_URL:", settings.base_url)

    # ---------- HEADLESS INTELIGENTE ----------
    if is_cloud_run():
        print("☁️ Cloud Run detectado → Headless TRUE")
        launch_headless = True
    else:
        print("💻 Ejecución local → headless =", settings.headless)
        launch_headless = settings.headless if settings.headless is not None else False

    # Lanzar navegador
    browser = playwright[settings.browser].launch(
        headless=launch_headless,
        args=["--disable-web-security"],  # opcional
    )

    # Crear contexto
    context = browser.new_context(
        base_url=settings.base_url,
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
    )

    context.set_default_timeout(settings.default_timeout)
    page = context.new_page()

    yield page

    context.close()
    browser.close()


# ============================================================
# ❌ Desactivar plugins que interfieren (pytest-playwright)
# ============================================================
def pytest_configure(config):
    # Desactivar plugin pytest-playwright si está presente
    try:
        config.pluginmanager.set_blocked("pytest_playwright")
        print("❌ Plugin pytest_playwright bloqueado correctamente")
    except Exception:
        pass

    # Desactivar plugin base_url
    try:
        config.pluginmanager.set_blocked("base_url")
        print("❌ Plugin pytest-base-url bloqueado correctamente")
    except Exception:
        pass
