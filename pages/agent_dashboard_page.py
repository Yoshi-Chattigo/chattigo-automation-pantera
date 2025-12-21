from pages.base_page import BasePage

class AgentDashboardPage(BasePage):
    POPUP_ENTENDIDO_BUTTON = "ch-ui-widget-generic-modal button:has-text('Entendido')" # Specific selector from codegen
    CHATS_HEADER = "text='Chats del agente'"

    NAV_BAR = "nav"
    TOGGLE_BUTTON = "xpath=/html/body/app-root/app-pages/app-main-dashboard/div[1]/nav/button"
    LOGOUT_BUTTON = "text='Cerrar Sesión'"
    
    # Status and Timer Selectors
    # Status and Timer Selectors
    STATUS_BUTTON = "xpath=/html/body/app-root/app-pages/app-main-dashboard/div[1]/app-agent-console/agent-console/div[1]/div[1]/div[1]/session-control/div/div[1]/div[2]/state-selector/button"
    SESSION_TIMER = "xpath=/html/body/app-root/app-pages/app-main-dashboard/div[1]/app-agent-console/agent-console/div[1]/div[1]/div[1]/session-control/div/div[2]/div[1]/span[2]/timer-count/span"
    PAUSE_TIMER = "xpath=/html/body/app-root/app-pages/app-main-dashboard/div[1]/app-agent-console/agent-console/div[1]/div[1]/div[1]/session-control/div/div[2]/div[2]/span[2]/timer-count/span"
    STATUS_SUCCESS_MESSAGE = "xpath=/html/body/app-root/app-pages/app-main-dashboard/div[1]/app-agent-console/agent-console/ch-ui-alerts/div/ch-ui-snackbar/div"
    STATUS_SUCCESS_CLOSE_BUTTON = "xpath=/html/body/app-root/app-pages/app-main-dashboard/div[1]/app-agent-console/agent-console/ch-ui-alerts/div/ch-ui-snackbar/div/div[2]/button/span"

    def handle_popup(self):
        """
        Checks if the 'Entendido' popup is visible and clicks it.
        Uses a polling loop to handle variable appearance times (especially for agente_1).
        """
        self.logger.info("Starting popup handling loop (10s)...")
        start_time = time.time()
        timeout = 10
        
        while time.time() - start_time < timeout:
             found_button = None
             
             # Strategy 1: Specific Modal Selector (Most precise)
             try:
                 btn = self.page.get_by_role("button", name="Entendido")
                 if btn.is_visible():
                     found_button = btn
                     self.logger.info("Popup found via role 'button' name 'Entendido'")
             except:
                 pass
     
             # Strategy 2: User provided XPath (Fallback) - "Entendido" Button
             if not found_button:
                 try:
                     xpath_ok = "/html/body/app-root/app-pages/app-main-dashboard/ch-ui-widget-generic-modal/div/div[2]/div/div[2]/div/div[1]/button"
                     btn = self.page.locator(xpath_ok)
                     if btn.is_visible():
                         found_button = btn
                         self.logger.info("Popup found via user provided XPath (OK button)")
                 except:
                     pass
     
             # Strategy 3: User provided XPath (Fallback) - "Close" (X) Button
             if not found_button:
                 try:
                     xpath_close = "/html/body/app-root/app-pages/app-main-dashboard/ch-ui-widget-generic-modal/div/div[2]/button/span"
                     btn = self.page.locator(xpath_close)
                     if btn.is_visible():
                         found_button = btn
                         self.logger.info("Popup found via user provided XPath (Close button)")
                 except:
                     pass
             
             # Action
             if found_button:
                 try:
                     self.logger.info("Clicking popup button...")
                     found_button.click(force=True)
                     found_button.wait_for(state="hidden", timeout=5000)
                     self.logger.info("Popup closed successfully.")
                     return # Exit loop if closed
                 except Exception as e:
                     self.logger.warning(f"Failed to click popup: {e}. Retrying...")
             
             # Wait a bit before next check
             self.page.wait_for_timeout(500)
             
        self.logger.info("Popup detection loop ended. No popup found or closed.")

    def is_chats_header_visible(self) -> bool:
        # Wait for the header to be visible
        try:
            self.page.wait_for_selector(self.CHATS_HEADER, state="visible", timeout=10000)
            return True
        except:
            return False

    def get_status_text(self) -> str:
        """Gets the text of the current status button."""
        self.page.wait_for_selector(self.STATUS_BUTTON, state="visible", timeout=10000)
        return self.page.inner_text(self.STATUS_BUTTON).strip()

    def set_status(self, status_name: str):
        """
        Sets the agent status.
        Args:
            status_name: The name of the status to select (e.g., 'Descanso', 'Online').
        """
        self.logger.info(f"Setting status to: {status_name}")
        # Wait for button to be stable
        self.page.wait_for_selector(self.STATUS_BUTTON, state="visible", timeout=10000)
        self.page.wait_for_timeout(500) # Small wait for stability
        
        # Force click to ensure it opens even if something is slightly overlapping
        self.click(self.STATUS_BUTTON, force=True)
        
        # Wait for dropdown/options to appear. Assuming standard behavior.
        # Using text matching for the option.
        option_selector = f"button:has-text('{status_name}')" 
        # Note: If options are not buttons, we might need a more generic selector like "li" or "div".
        # But usually in these apps they are buttons or list items.
        # Let's try to find it.
        self.page.wait_for_selector(option_selector, state="visible", timeout=5000)
        self.click(option_selector)
        self.logger.info(f"Clicked status option: {status_name}")
        # Wait for UI to settle and message to appear
        self.page.wait_for_timeout(2000)

    def is_timer_visible(self) -> bool:
        """Checks if the session timer is visible."""
        return self.page.is_visible(self.SESSION_TIMER)

    def get_timer_value(self) -> str:
        """Gets the current value of the session timer."""
        self.page.wait_for_selector(self.SESSION_TIMER, state="visible", timeout=10000)
        return self.page.inner_text(self.SESSION_TIMER).strip()

    def get_pause_timer_value(self) -> str:
        """Gets the current value of the pause timer."""
        # This timer might only be visible when in pause/break.
        if self.page.is_visible(self.PAUSE_TIMER):
            return self.page.inner_text(self.PAUSE_TIMER).strip()
        return "00:00:00" # Or None, or empty string

    def verify_status_message(self) -> bool:
        """Verifies if the status update success message appears and closes it."""
        try:
            self.logger.info("Waiting for status success message...")
            self.page.wait_for_selector(self.STATUS_SUCCESS_MESSAGE, state="visible", timeout=10000)
            
            # Click close button if available
            if self.page.is_visible(self.STATUS_SUCCESS_CLOSE_BUTTON):
                self.logger.info("Closing status success message...")
                self.page.wait_for_timeout(500) # Wait a bit before closing
                self.click(self.STATUS_SUCCESS_CLOSE_BUTTON, force=True)
                self.page.wait_for_selector(self.STATUS_SUCCESS_MESSAGE, state="hidden", timeout=5000)
            
            return True
        except Exception as e:
            self.logger.error(f"Status message verification failed: {e}")
            return False

    def logout(self):
        """
        Performs the logout action by expanding the side menu.
        """
        self.logger.info("Attempting to logout...")
        
        try:
            # 1. Hover over nav bar to ensure it's active
            self.logger.info("Hovering over navigation bar...")
            self.page.hover(self.NAV_BAR)
            self.page.wait_for_timeout(500)

            # 2. Click the toggle button to expand the menu
            self.logger.info("Clicking toggle button to expand menu...")
            self.click(self.TOGGLE_BUTTON)
            self.page.wait_for_timeout(1000) # Wait for animation

            # 3. Click Logout
            self.logger.info("Waiting for 'Cerrar Sesión' button...")
            self.page.wait_for_selector(self.LOGOUT_BUTTON, state="visible", timeout=5000)
            self.click(self.LOGOUT_BUTTON)
            self.logger.info("Logout clicked successfully.")

        except Exception as e:
            self.logger.error(f"Logout failed: {e}")
            raise e
    def finalize_chat(self, reason: str = "Cierre"):
        """
        Finalizes the current chat.
        Args:
            reason: The reason for closing the chat (e.g., 'Cierre').
        """
        self.logger.info("Initiating chat finalization...")
        
        # 1. Click 'Finalizar' button
        self.logger.info("Clicking 'Finalizar' button...")
        self.page.get_by_role("button", name="Finalizar").click()
        
        # 2. Select reason from the list
        self.logger.info(f"Selecting reason: {reason}")
        # Wait for the modal/list to appear
        self.page.wait_for_timeout(1000) 
        self.page.get_by_role("listitem").filter(has_text=reason).click()
        
        # 3. Confirm 'Finalizar chat'
        self.logger.info("Confirming 'Finalizar chat'...")
        self.page.locator("a").filter(has_text="Finalizar chat").click()
        
        self.logger.info("Chat finalized successfully.")
