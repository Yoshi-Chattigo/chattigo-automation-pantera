from pages.base_page import BasePage

class LoginPage(BasePage):
    USERNAME_INPUT = "input[placeholder='Usuario']"
    PASSWORD_INPUT = "input[placeholder='Contraseña']"
    LOGIN_BUTTON = "#loginButton"
    ERROR_MESSAGE = "text='Login incorrecto, intente de nuevo.'"

    def login(self, username, password, retries=3):
        for attempt in range(1, retries + 1):
            try:
                self.logger.info(f"Starting login process (Attempt {attempt}/{retries})")
                self.page.wait_for_selector(self.USERNAME_INPUT, state="visible", timeout=10000)
                self.fill(self.USERNAME_INPUT, username)
                
                self.logger.info("Username filled, waiting for password field")
                self.page.wait_for_selector(self.PASSWORD_INPUT, state="visible", timeout=10000)
                self.fill(self.PASSWORD_INPUT, password)
                
                self.logger.info("Password filled, clicking login button")
                self.click(self.LOGIN_BUTTON)
                
                # If we get here without exception, break the loop
                # (Note: Verification is usually done outside, but we can assume click worked)
                self.logger.info(f"Login click successful on attempt {attempt}")
                return
            except Exception as e:
                self.logger.warning(f"Login attempt {attempt} failed: {e}")
                if attempt == retries:
                    self.logger.error("Max retries reached for login.")
                    raise e
                self.page.wait_for_timeout(2000) # Wait before retry
                self.page.reload() # Reload page to reset state

    def get_error_message(self):
        return self.get_text(self.ERROR_MESSAGE)
