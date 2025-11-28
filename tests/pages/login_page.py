from tests.pages.base_page import BasePage
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class LoginPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    # ==========================
    # ABRIR LA PÁGINA DE LOGIN
    # ==========================
    def open(self):
        self.goto("/login/pages/login")

    # ==========================
    # FLUJO DE LOGIN
    # ==========================
    def login(self, username, password):
        print("➡ Llenando usuario y contraseña…")

        # Campos correctos de Pantera:
        self.fill("input[formcontrolname='user']", username)
        self.fill("input[formcontrolname='password']", password)

        print("➡ Click en botón INGRESAR…")
        self.click("#loginButton")

        # Intentar navegación estándar
        if not self.wait_for_login_redirect():
            print("⚠ Primer intento falló. Reintentando login…")
            self.click("#loginButton")
            self.wait_for_login_redirect()

    # ==========================
    # ESPERAR REDIRECCIÓN
    # ==========================
    def wait_for_login_redirect(self):
        try:
            self.page.wait_for_url("**/dashboard/**", timeout=10000)
            print("🟢 Navegación exitosa al dashboard.")
            self.handle_password_popup()
            return True
        except PlaywrightTimeoutError:
            print("❌ No navegó al dashboard en el tiempo esperado.")
            return False

    # ==========================
    # CERRAR POPUP DE CAMBIO DE CONTRASEÑA
    # ==========================
    def handle_password_popup(self):
        try:
            self.page.click("button:has-text('Entendido')", timeout=3000)
            print("🟢 Popup de contraseña cerrado.")
        except PlaywrightTimeoutError:
            pass  # No apareció → todo bien

    # ==========================
    # VALIDAR SI EL LOGIN FUE EXITOSO
    # ==========================
    def is_logged(self):
        try:
            self.page.wait_for_selector("app-main-dashboard", timeout=10000)
            print("🟢 Dashboard detectado.")
            return True
        except PlaywrightTimeoutError:
            print("❌ Dashboard no encontrado.")
            return False
