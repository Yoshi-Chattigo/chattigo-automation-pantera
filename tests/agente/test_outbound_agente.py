import pytest
import os
import re
from config.config import Config
from pages.login_page import LoginPage
from pages.agent_dashboard_page import AgentDashboardPage
from pages.outbound_page import OutboundPage
from playwright.sync_api import expect

@pytest.mark.smoke
def test_bienvenida_rapida(page):
    # Initialize pages
    login_page = LoginPage(page)
    dashboard_page = AgentDashboardPage(page)
    outbound_page = OutboundPage(page)
    
    # 1. Login
    login_page.navigate(Config.BASE_URL)
    login_page.login(Config.USERNAME, Config.PASSWORD)
    
    # Verify login success (optional but good practice)
    expect(page).to_have_url(re.compile(".*dashboard"), timeout=30000)
    
    # Handle initial popup
    dashboard_page.handle_popup()
    
    # 2. Navigate to Outbound
    outbound_page.navigate_to_outbound()
    
    # 3. Select Campaign
    outbound_page.select_campaign("Campaña automation")
    
    # 3.1 Select Channel (as per codegen)
    outbound_page.select_channel("5215639549198")
    
    # 4. Upload Contact List
    # Construct absolute path to the file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "utils", "Plantilla_HSM .xlsx")
    
    outbound_page.upload_contact_list(file_path)
    
    # 5. Select Template
    outbound_page.select_template("bienvenida_rapida_auto")
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success (optional, maybe check if redirected or success message persists)
    # For now, the method send_outbound handles the success modal.
