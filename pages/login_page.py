import re
from pages.base_page import BasePage

class LoginPage(BasePage):
    USERNAME_INPUT = "input[placeholder='Usuario']"
    PASSWORD_INPUT = "input[placeholder='Contraseña']"
    LOGIN_BUTTON = "#loginButton"
    # Selector for "Session already active" popup if it exists, or just generic error
    ERROR_MESSAGE = "text='Login incorrecto, intente de nuevo.'"

    def login(self, username, password, retries=3):
        for attempt in range(1, retries + 1):
            try:
                self.logger.info(f"Starting login process (Attempt {attempt}/{retries})")
                
                # Check if we are already logged in (optional optimization)
                if "dashboard" in self.page.url:
                     self.logger.info("Already on dashboard.")
                     return

                self.page.wait_for_selector(self.USERNAME_INPUT, state="visible", timeout=10000)
                self.fill(self.USERNAME_INPUT, username)
                
                self.logger.info("Username filled, waiting for password field")
                self.page.wait_for_selector(self.PASSWORD_INPUT, state="visible", timeout=10000)
                self.fill(self.PASSWORD_INPUT, password)
                
                self.logger.info("Password filled, clicking login button")
                self.click(self.LOGIN_BUTTON)
                
                # Validation inside retry loop
                try:
                    # Wait for either dashboard URL OR an error message
                    # We expect dashboard
                    self.page.wait_for_url(re.compile(".*dashboard"), timeout=15000)
                    self.logger.info(f"Login successful on attempt {attempt}")
                    return
                except:
                    # If we didn't get to dashboard, check for error message
                    if self.page.is_visible(self.ERROR_MESSAGE):
                         self.logger.warning("Login failed: Incorrect credentials message displayed.")
                    else:
                         self.logger.warning("Login failed: Navigation to dashboard timed out.")
                    raise Exception("Login verification failed")
                
            except Exception as e:
                self.logger.warning(f"Login attempt {attempt} failed: {e}")
                if attempt == retries:
                    self.logger.error("Max retries reached for login.")
                    raise e
                
                self.logger.info("Reloading page before retry...")
                self.page.reload()
                self.page.wait_for_load_state("networkidle")

    def get_error_message(self):
        return self.get_text(self.ERROR_MESSAGE)
