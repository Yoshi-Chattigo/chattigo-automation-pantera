from playwright.sync_api import Page
from pages.base_page import BasePage
import os

class OutboundPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Selectors
        self.OUTBOUND_MENU = "text=Outbound"
        self.SEND_OUTBOUND_SUBMENU = "text=Enviar Outbound"
        self.CAMPAIGN_DROPDOWN = "#campaign button:has-text('Seleccionar')"
        self.CAMPAIGN_OPTION = "p:has-text('PruebasQA Hija 1')"
        self.ATTACH_CONTACTS_BUTTON = "button:has-text('Adjuntar lista de contactos')"
        self.SELECT_FILE_TEXT = "text=Selecciona un archivo"
        self.SAVE_BUTTON = "button:has-text('Guardar')"
        self.TEMPLATE_DROPDOWN = "button:has-text('Seleccionar...')"
        self.TEMPLATE_SEARCH_INPUT = "input[placeholder='Buscar...']"
        self.TEMPLATE_OPTION = "button:has-text('bienvenida_rapida_hija1 -')"

    def navigate_to_outbound(self):
        self.logger.info("Navigating to Outbound > Enviar Outbound")
        # Expand sidebar using specific selector from AgentDashboardPage
        # Hover first as in logout
        self.page.wait_for_selector("nav", state="visible", timeout=20000)
        self.page.hover("nav")
        self.page.wait_for_timeout(500)
        
        toggle_button = "xpath=/html/body/app-root/app-pages/app-main-dashboard/div[1]/nav/button"
        self.click(toggle_button, force=True) 
        self.page.wait_for_timeout(1000) # Wait for animation
        
        self.click(self.OUTBOUND_MENU)
        self.click(self.SEND_OUTBOUND_SUBMENU)

    def select_campaign(self, campaign_name: str):
        self.logger.info(f"Selecting campaign: {campaign_name}")
        self.click(self.CAMPAIGN_DROPDOWN)
        # Using dynamic selector for campaign name if needed, but using fixed for now based on codegen
        self.click(f"p:has-text('{campaign_name}')")
        # Wait for the UI to update after selection
        self.page.wait_for_timeout(1000)

    def select_channel(self, channel_name: str):
        self.logger.info(f"Selecting channel: {channel_name}")
        # Wait for the UI to update after campaign selection
        self.page.wait_for_timeout(2000)
        
        # Try to click the 'Seleccionar' button. 
        # Using a more specific context if possible, or just the generic one that appears next in flow.
        self.logger.info("Opening Channel dropdown...")
        self.click("button:has-text('Seleccionar')", force=True)
        
        # Wait for the option to appear explicitly
        self.logger.info(f"Waiting for channel option containing: {channel_name}")
        
        # Use strictly generic locator + filter as per codegen to avoid specific tag issues if p changed
        # Codegen: page.get_by_role("paragraph").filter(has_text="5215639549198").click()
        try:
            option_locator = self.page.get_by_role("paragraph").filter(has_text=channel_name)
            option_locator.wait_for(state="visible", timeout=30000)
            option_locator.click()
        except Exception as e:
             self.logger.warning(f"Standard click failed: {e}. Retrying with force=True")
             self.page.get_by_role("paragraph").filter(has_text=channel_name).click(force=True)
             
        self.page.wait_for_timeout(1000)
        
        # Verify selection or retry? For now, just ensuring dropdown is closed might be enough?
        # Or simply waiting a bit more for the UI to update.
        self.page.wait_for_timeout(2000)

    def upload_contact_list(self, file_path: str):
        self.logger.info(f"Uploading contact list from: {file_path}")
        # Wait for button to be visible
        self.page.wait_for_selector(self.ATTACH_CONTACTS_BUTTON, state="visible", timeout=30000)
        self.click(self.ATTACH_CONTACTS_BUTTON)
        
        # Handle file upload using file chooser event
        with self.page.expect_file_chooser() as fc_info:
            self.click(self.SELECT_FILE_TEXT)
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        
        # Wait for file to be processed
        # Increased wait for Cloud Run environment
        self.page.wait_for_timeout(5000)
        
        # 1. Click 'Guardar' in the upload modal
        self.logger.info("Clicking first 'Guardar' (Modal)")
        try:
             self.page.locator("div[role='dialog'] button").filter(has_text="Guardar").click()
        except Exception:
             self.logger.warning("Modal Guardar not found via specific selector, trying generic.")
             self.page.get_by_role("button", name="Guardar").first.click(force=True)
        
        self.page.wait_for_timeout(2000)
        
        # 2. Click 'Guardar' to continue (Contact List Section)
        self.logger.info("Clicking second 'Guardar' (Contact List Section)")
        try:
             self.page.locator("#scrollbar").get_by_text("Guardar").click()
        except Exception:
             self.logger.warning("Scrollbar Guardar not found, trying generic.")
             self.page.get_by_role("button", name="Guardar").click(force=True)
        
        self.page.wait_for_timeout(2000)

    def select_template(self, template_name: str, attachment_path: str = None, attachment_url: str = None):
        self.logger.info(f"Selecting template: {template_name}")
        
        self.page.keyboard.press("PageDown")
        self.page.wait_for_timeout(1000)
        
        # Use get_by_role as per codegen
        # Add wait to ensure button is interactable
        self.logger.info("Opening Template dropdown...")
        self.page.get_by_role("button", name="Seleccionar...").click(force=True)
        
        # Wait for input to be visible
        self.page.wait_for_selector(self.TEMPLATE_SEARCH_INPUT, state="visible", timeout=5000)
        
        self.logger.info(f"Searching for template: {template_name}")
        # Clear input first just in case
        self.page.locator(self.TEMPLATE_SEARCH_INPUT).clear()
        # Use type with delay to ensure the frontend filter triggers correctly
        search_term = "bien" if "bienvenida" in template_name else "qa"
        if "documento_url" in template_name:
             search_term = "docu" 
        elif "imagen_url" in template_name:
             search_term = "qa_imagen_url"
        elif "video_url" in template_name:
             search_term = "qa_video_url"
        
        self.page.locator(self.TEMPLATE_SEARCH_INPUT).type(search_term, delay=100)
        
        # Determine the dynamic selector based on the template name provided
        template_selector = f"button:has-text('{template_name}')"
        
        # Wait for the option to appear
        self.logger.info(f"Waiting for template option: {template_selector}")
        self.page.wait_for_selector(template_selector, state="visible", timeout=10000)
        
        self.logger.info(f"Clicking template option: {template_selector}")
        self.click(template_selector, force=True)
        
        self.page.wait_for_timeout(1000)

        # Handle Attachment (File)
        if attachment_path:
            self.logger.info(f"Uploading attachment from: {attachment_path}")
            
            # Ensure the file exists before trying to upload
            if not os.path.exists(attachment_path):
                raise FileNotFoundError(f"Attachment file not found at: {attachment_path}")

            # Using force=True for robustness
            attach_btn_name = "Adjunta un archivo"
            try:
                self.logger.info("Waiting for file chooser event...")
                with self.page.expect_file_chooser() as fc_info:
                    # Click the button to trigger the file dialog
                    self.page.get_by_role("button", name=attach_btn_name).click(force=True)
                
                file_chooser = fc_info.value
                self.logger.info(f"File chooser opened. Setting files: {attachment_path}")
                file_chooser.set_files(attachment_path)
                
                self.logger.info("Attachment uploaded successfully.")
                self.page.wait_for_timeout(2000) # Wait for upload
            except Exception as e:
                self.logger.error(f"Error uploading attachment: {e}")
                raise e
        
        # Handle Attachment (URL)
        if attachment_url:
            self.logger.info(f"Setting attachment URL: {attachment_url}")
            try:
                # Click 'escribe una URL' using text locator as per codegen
                self.page.get_by_text("escribe una URL").click(force=True)
                
                # Fill the textbox
                # Codegen used generic get_by_role("textbox"). We should be careful if there are multiple.
                # Assuming this appears after clicking 'escribe una URL'.
                self.page.wait_for_timeout(500)
                # It seems it might be the only visible textbox in that context, or we can look for it.
                # Let's try filling the focused one or the one that appeared.
                self.page.get_by_role("textbox").last.fill(attachment_url)
                
                self.logger.info("Attachment URL set successfully.")
                self.page.wait_for_timeout(1000)
            except Exception as e:
                self.logger.error(f"Error setting attachment URL: {e}")
                raise e
        

        
        # Click 'Guardar' for Template Section
        self.logger.info("Clicking 'Guardar' (Template Section)")
        
        # User requested alignment with Codegen: page.locator("a").filter(has_text="Guardar").click()
        # Removing .last to rely on specific unique element or strict mode finding
        try:
             self.page.locator("a").filter(has_text="Guardar").click()
        except Exception as e:
             self.logger.warning(f"Strict Guardar click failed (maybe multiple?): {e}. Retrying with force=True")
             self.page.locator("a").filter(has_text="Guardar").click(force=True)
        
        # KEY FIX: Wait for the template search input to disappear. 
        # This confirms the section closed and the next one (Agent) should appear.
        try:
            self.page.locator(self.TEMPLATE_SEARCH_INPUT).wait_for(state="hidden", timeout=5000)
            self.logger.info("Template section saved successfully (Search input hidden)")
        except:
             self.logger.warning("Template search input still visible? attempting to proceed anyway.")
             # Retry click if needed
             self.logger.info("Retrying 'Guardar' click with specific XPath...")
             self.page.locator(guardar_xpath).click(force=True)
             self.page.locator(self.TEMPLATE_SEARCH_INPUT).wait_for(state="hidden", timeout=5000)
        
        # Increase wait to ensure next section (Agent) renders
        self.page.wait_for_timeout(2000)

    def select_agent(self, agent_option: str = "Yo"):
        self.logger.info(f"Selecting agent: {agent_option}")
        self.page.keyboard.press("PageDown")
        self.page.wait_for_timeout(2000) # Increased wait before interaction
        
        self.logger.info("Attempting to open Agent dropdown...")
        
        try:
             # Force click explicitly on the last 'Seleccionar' button which corresponds to Agent
             self.page.get_by_role("button", name="Seleccionar...").last.click(force=True)
             self.page.wait_for_timeout(1000)
             
             # Check if option is visible, if not try again
             if not self.page.get_by_role("button", name=agent_option).is_visible():
                  self.logger.warning("Agent option not visible, retrying dropdown click...")
                  self.page.get_by_role("button", name="Seleccionar...").last.click(force=True)
                  self.page.wait_for_timeout(1000)

             self.logger.info(f"Clicking agent option: {agent_option}")
             self.page.get_by_role("button", name=agent_option).click(force=True)
             
        except Exception as e:
             self.logger.error(f"Error selecting agent: {e}")
             raise e

        self.page.wait_for_timeout(1000)
        
        # Click 'Guardar' for Agent Section
        # Codegen: page.locator("#scrollbar").get_by_text("Guardar").click()
        self.logger.info("Clicking 'Guardar' (Agent Section)")
        self.page.locator("#scrollbar").get_by_text("Guardar").click()
        self.page.wait_for_timeout(1000)

    def send_outbound(self):
        self.logger.info("Sending Outbound")
        self.page.get_by_role("button", name="ENVIAR OUTBOUND").click()
        
        # Handle Success Modal
        self.logger.info("Handling Success Modal")
        self.page.get_by_role("button", name="Entendido").click()
        
        # Handle Toast/Close if needed (Codegen showed closing a toast/notification)
        # page.get_by_role("button", name="Cerrar").click()
        try:
            self.page.get_by_role("button", name="Cerrar").click(timeout=3000)
        except:
            pass
