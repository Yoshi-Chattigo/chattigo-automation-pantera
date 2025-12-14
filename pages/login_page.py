from pages.base_page import BasePage

class LoginPage(BasePage):
    USERNAME_INPUT = "input[placeholder='Usuario']"
    PASSWORD_INPUT = "input[placeholder='Contraseña']"
    LOGIN_BUTTON = "#loginButton"
    ERROR_MESSAGE = "text='Login incorrecto, intente de nuevo.'"

    def login(self, username, password):
        self.logger.info("Starting login process")
        self.page.wait_for_selector(self.USERNAME_INPUT, state="visible", timeout=10000)
        self.fill(self.USERNAME_INPUT, username)
        self.logger.info("Username filled, waiting for password field")
        self.page.wait_for_selector(self.PASSWORD_INPUT, state="visible", timeout=10000)
        self.fill(self.PASSWORD_INPUT, password)
        self.logger.info("Password filled, clicking login button")
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self):
        return self.get_text(self.ERROR_MESSAGE)
