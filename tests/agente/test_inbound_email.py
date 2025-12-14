import pytest
import time
from config.config import Config
from pages.login_page import LoginPage
from pages.agent_dashboard_page import AgentDashboardPage
from utils.email_sender import EmailSender
from playwright.sync_api import expect
import re

@pytest.mark.email
def test_receive_email(page):
    # 1. Send Email
    email_sender = EmailSender()
    subject = f"Test Automation Email {time.time()}"
    body = "This is a test email sent by the automation framework."
    to_email = "qapantera@chattigo.com"
    
    # Ensure credentials are set before running
    email_sender.send_email(subject, body, to_email)
    # Commented out to prevent failure if creds are missing during initial run
    # User needs to configure env vars first
    
    # 2. Login
    login_page = LoginPage(page)
    dashboard_page = AgentDashboardPage(page)
    
    login_page.navigate(Config.BASE_URL)
    login_page.login(Config.USERNAME, Config.PASSWORD)
    
    # Verify Dashboard & Handle Popup (matching test_agent_status.py)
    try:
        expect(page).to_have_url(re.compile(".*dashboard/agent"), timeout=30000)
    except AssertionError:
        if page.is_visible(login_page.ERROR_MESSAGE):
            error_text = login_page.get_text(login_page.ERROR_MESSAGE)
            raise AssertionError(f"Login failed with error: {error_text}")
        raise

    dashboard_page.handle_popup()
    
    # 3. Verify Email in Dashboard
    # Emails can take a minute or two to arrive and process.
    print(f"Waiting for email with subject: {subject}")
    
    # Wait for the chat item to appear in the list (Left side)
    # Use a more robust selector targeting the chat-card component
    print(f"Waiting for chat card from: {email_sender.sender_email}")
    
    # Filter by sender email as requested by user
    chat_card = page.locator("chat-card").filter(has_text=email_sender.sender_email).first
    
    # We expect this specific card to appear
    expect(chat_card).to_be_visible(timeout=60000)

    print("Email received! Clicking to view details...")
    
    # Click the chat to open details
    chat_card.click()
    
    # Verify content in the detail view (Right side)
    # Assuming the subject also appears in the header of the detail view
    print("Verifying detail view...")
    # Be specific to avoid ambiguity with the left list. 
    # Usually the detail view has a specific container, but for now we look for the text again 
    # and ensure it's visible. Since we clicked it, it should be active.
    # We can also check for the body text if it's visible in the preview or detail.
    expect(page.locator(f"text={body}").first).to_be_visible(timeout=10000)
    
    print("Email content verified successfully!")

@pytest.mark.email
def test_chat_closure(page):
    # 1. Send Email (to ensure there is a chat to close)
    email_sender = EmailSender()
    subject = f"Test Automation Closure {time.time()}"
    body = "This is a test email for chat closure."
    to_email = "qapantera@chattigo.com"
    
    email_sender.send_email(subject, body, to_email)
    
    # 2. Login
    login_page = LoginPage(page)
    dashboard_page = AgentDashboardPage(page)
    
    login_page.navigate(Config.BASE_URL)
    login_page.login(Config.USERNAME, Config.PASSWORD)
    
    dashboard_page.handle_popup()
    
    # 3. Find and Open Chat
    print(f"Waiting for chat card from: {email_sender.sender_email}")
    chat_card = page.locator("chat-card").filter(has_text=email_sender.sender_email).first
    expect(chat_card).to_be_visible(timeout=60000)
    chat_card.click()
    
    # 4. Finalize Chat
    print("Finalizing chat...")
    dashboard_page.finalize_chat()
