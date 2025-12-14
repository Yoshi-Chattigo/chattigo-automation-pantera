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
        # Wait for the second dropdown to be ready
        self.page.wait_for_timeout(1000)
        
    def select_channel(self, channel_name: str):
        self.logger.info(f"Selecting channel: {channel_name}")
        # Wait for the UI to update after campaign selection
        self.page.wait_for_timeout(1000)
        
        # Try to click the 'Seleccionar' button. 
        # Reverting to simple selector as nth=1 failed.
        # Assuming the campaign dropdown text changed to the selected campaign.
        self.click("button:has-text('Seleccionar')", force=True)
        self.page.wait_for_timeout(500)
        self.click(f"p:has-text('{channel_name}')", force=True)
        self.page.wait_for_timeout(1000)

    def upload_contact_list(self, file_path: str):
        self.logger.info(f"Uploading contact list from: {file_path}")
        # Wait for button to be visible
        self.page.wait_for_selector(self.ATTACH_CONTACTS_BUTTON, state="visible", timeout=10000)
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
        self.page.get_by_role("button", name="Guardar").click(force=True)
        
        self.page.wait_for_timeout(2000)
        
        # 2. Click 'Guardar' to continue (Contact List Section)
        self.logger.info("Clicking second 'Guardar' (Contact List Section)")
        self.page.locator("#scrollbar").get_by_text("Guardar").click(force=True)
        
        self.page.wait_for_timeout(2000)

    def select_template(self, template_name: str):
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
        self.page.locator(self.TEMPLATE_SEARCH_INPUT).type("bien", delay=100) 
        
        # Determine the dynamic selector based on the template name provided
        template_selector = f"button:has-text('{template_name}')"
        
        # Wait for the option to appear
        self.logger.info(f"Waiting for template option: {template_selector}")
        self.page.wait_for_selector(template_selector, state="visible", timeout=10000)
        
        self.logger.info(f"Clicking template option: {template_selector}")
        self.click(template_selector, force=True)
        
        self.page.wait_for_timeout(1000)
        
        # Click 'Guardar' for Template Section
        # Codegen: page.locator("a").filter(has_text="Guardar").click()
        self.logger.info("Clicking 'Guardar' (Template Section)")
        # Click 'Guardar' for Template Section
        self.logger.info("Clicking 'Guardar' (Template Section)")
        self.page.locator("a").filter(has_text="Guardar").click(force=True)
        
        # KEY FIX: Wait for the template search input to disappear. 
        # This confirms the section closed and the next one (Agent) should appear.
        try:
            self.page.locator(self.TEMPLATE_SEARCH_INPUT).wait_for(state="hidden", timeout=5000)
            self.logger.info("Template section saved successfully (Search input hidden)")
        except:
             self.logger.warning("Template search input still visible? attempting to proceed anyway.")
        
        # Increase wait to ensure next section (Agent) renders
        self.page.wait_for_timeout(2000)

    def select_agent(self, agent_option: str = "Yo"):
        self.logger.info(f"Selecting agent: {agent_option}")
        self.page.keyboard.press("PageDown")
        
        self.logger.info("Attempting to open Agent dropdown...")
        try:
            # Try XPath which is sometimes more robust for 'text' content in headless
            # getting the LAST one visible
            xpath_selector = "(//button[contains(., 'Seleccionar...')])[last()]"
            self.page.locator(xpath_selector).click(force=True, timeout=5000)
        except Exception as e:
             self.logger.error(f"XPath strategy failed: {e}. Trying generic get_by_role.")
             self.page.get_by_role("button", name="Seleccionar...").last.click(force=True)

        self.page.wait_for_timeout(1000)
        
        # Select Option
        self.logger.info(f"Clicking agent option: {agent_option}")
        self.page.get_by_role("button", name=agent_option).click(force=True)
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
