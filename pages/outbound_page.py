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
        self.page.wait_for_timeout(2000)
        
        # Strategy: Target the specific dropdown for Channel
        # If we can't find a unique ID, we search for the 'Canal' label or similar context.
        # Since we don't have the full DOM, we'll try a more robust generic approach.
        
        # 1. Ensure any previous dropdown is closed (click body?) - skipping for now to avoid side effects
        
        # 2. Click "Seleccionar"
        # We assume the first "Seleccionar" (Campaign) might still be visible or changed text.
        # We'll try to click specifically the button that is *not* the campaign one if possible.
        # But simpler: click unique "Seleccionar" if text changed, or the *second* one.
        
        try:
            # Try to find the button associated with 'Canal' if label exists, otherwise wait carefully
            # Fallback: Click the button that has text "Seleccionar" and appear *after* the campaign one.
            # Using nth=1 is risky if campaign text changes to "Seleccionar" on deselection.
            # Best bet: Wait for campaign selector to NOT be "Seleccionar" (it should be the campaign name).
            
            # Wait for campaign selection to be applied (text change)
            self.page.wait_for_function("document.querySelector('#campaign button').innerText !== 'Seleccionar'", timeout=5000)
        except:
            self.logger.warning("Campaign button text might not have updated or selector differs.")

        # Now click the active "Seleccionar"
        # We explicitly wait for it to be enabled
        btn_selector = "button:has-text('Seleccionar')"
        self.page.wait_for_selector(btn_selector, state="visible", timeout=10000)
        
        # In headless, sometimes a force click is better for custom dropdowns
        self.click(btn_selector, force=True)
        self.page.wait_for_timeout(1000)
        
        # 3. Wait for option
        target_option = f"p:has-text('{channel_name}')"
        try:
            self.page.wait_for_selector(target_option, state="visible", timeout=10000)
            self.click(target_option, force=True)
        except Exception as e:
            self.logger.error(f"Failed to find channel option '{channel_name}'. Retrying dropdown click...")
            # Retry opening dropdown once
            self.click(btn_selector, force=True)
            self.page.wait_for_timeout(1000)
            self.click(target_option, force=True)

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
        self.page.wait_for_timeout(2000)
        
        # 1. Click 'Guardar' in the upload modal
        self.logger.info("Clicking first 'Guardar' (Modal)")
        # Use get_by_role as per codegen to ensure we target the correct button
        self.page.get_by_role("button", name="Guardar").click()
        
        self.page.wait_for_timeout(2000)
        
        # 2. Click 'Guardar' to continue (Contact List Section)
        # Using selector from codegen: page.locator("#scrollbar").get_by_text("Guardar")
        self.logger.info("Clicking second 'Guardar' (Contact List Section)")
        self.page.locator("#scrollbar").get_by_text("Guardar").click()
        
        self.page.wait_for_timeout(2000)

    def select_template(self, template_name: str):
        self.logger.info(f"Selecting template: {template_name}")
        
        # Scroll down using keyboard to ensure template dropdown is visible
        self.page.keyboard.press("PageDown")
        self.page.wait_for_timeout(500)
        
        # Use get_by_role as per codegen
        self.page.get_by_role("button", name="Seleccionar...").click()
        
        self.fill(self.TEMPLATE_SEARCH_INPUT, template_name)
        self.click(f"button:has-text('{template_name}')", force=True)
        
        self.page.wait_for_timeout(1000)
        
        # Click 'Guardar' for Template Section
        # Codegen: page.locator("a").filter(has_text="Guardar").click()
        self.logger.info("Clicking 'Guardar' (Template Section)")
        self.page.locator("a").filter(has_text="Guardar").click()
        self.page.wait_for_timeout(1000)

    def select_agent(self, agent_option: str = "Yo"):
        self.logger.info(f"Selecting agent: {agent_option}")
        self.page.keyboard.press("PageDown")
        self.page.wait_for_timeout(500)
        
        # Select Agent Dropdown
        # The codegen uses a complex locator or just the next "Seleccionar..." button.
        # Since we saved previous sections, hopefully this is the only active/visible "Seleccionar..." or the next one.
        # We'll try get_by_role("button", name="Seleccionar...") again.
        self.page.get_by_role("button", name="Seleccionar...").click()
        self.page.wait_for_timeout(500)
        
        # Select Option
        self.page.get_by_role("button", name=agent_option).click()
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
