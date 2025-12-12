import pytest
from config.config import Config
from playwright.sync_api import expect

from pages.agent_dashboard_page import AgentDashboardPage
import re

@pytest.mark.smoke
def test_valid_login(login_page):
    login_page.navigate(Config.BASE_URL)
    login_page.login(Config.USERNAME, Config.PASSWORD)
    
    # Wait for the URL to change to the dashboard
    expect(login_page.page).to_have_url(re.compile(".*dashboard/agent"), timeout=30000)
    
    dashboard_page = AgentDashboardPage(login_page.page)
    dashboard_page.handle_popup()
    
    assert dashboard_page.is_chats_header_visible(), "Dashboard header 'Chats del agente' not visible"

@pytest.mark.smoke
def test_logout_agente(login_page):
    # 1. Login
    login_page.navigate(Config.BASE_URL)
    login_page.login(Config.USERNAME, Config.PASSWORD)
    
    # 2. Verify Dashboard
    expect(login_page.page).to_have_url(re.compile(".*dashboard/agent"), timeout=30000)
    
    dashboard_page = AgentDashboardPage(login_page.page)
    dashboard_page.handle_popup()
    
    # 3. Logout
    dashboard_page.logout()
    
    # 4. Verify Redirection to Login
    # The URL usually contains 'login' after logout
    expect(login_page.page).to_have_url(re.compile(".*login"), timeout=10000)
