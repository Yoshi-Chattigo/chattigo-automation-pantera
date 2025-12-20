import pytest
import os
import re
from config.config import Config
from pages.login_page import LoginPage
from pages.agent_dashboard_page import AgentDashboardPage
from pages.outbound_page import OutboundPage
from playwright.sync_api import expect

@pytest.mark.smoke
def test_outbound_bienvenida_rapida(page):
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
    # Optimized in AgentDashboardPage to wait and retry if needed
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
    file_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(file_path)
    
    # 5. Select Template
    outbound_page.select_template("bienvenida_rapida_auto")
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success (optional, maybe check if redirected or success message persists)
    # For now, the method send_outbound handles the success modal.

@pytest.mark.smoke
def test_outbound_document(page):
    # Initialize pages
    login_page = LoginPage(page)
    dashboard_page = AgentDashboardPage(page)
    outbound_page = OutboundPage(page)
    
    # 1. Login
    login_page.navigate(Config.BASE_URL)
    login_page.login(Config.USERNAME, Config.PASSWORD)
    
    # Verify login success
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
    file_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(file_path)
    
    #5. Select Template (qa_documento) with Attachmen
    outbound_page.select_template("qa_documento", attachment_path=pdf_path)
    
   
    # Construct absolute path to the PDF in the utils folder
    pdf_path = os.path.join(base_dir, "utils", "Amicis, Edmundo De - Corazon.pdf")
   
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success handled by send_outbound

@pytest.mark.smoke
def test_outbound_image(page):
    # Initialize pages
    login_page = LoginPage(page)
    dashboard_page = AgentDashboardPage(page)
    outbound_page = OutboundPage(page)
    
    # 1. Login
    login_page.navigate(Config.BASE_URL)
    login_page.login(Config.USERNAME, Config.PASSWORD)
    
    # Verify login success
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
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    contact_list_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(contact_list_path)
    
    # 5. Select Template (qa_imagen) with Attachment
    # Construct absolute path to the Image in the utils folder
    image_path = os.path.join(base_dir, "utils", "imagen.png")
    
    outbound_page.select_template("qa_imagen", attachment_path=image_path)

    # Construct absolute path to the PDF in the utils folder
    pdf_path = os.path.join(base_dir, "utils", "Tinting_Home_Windows.jpg")
    
     # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success handled by send_outbound

@pytest.mark.smoke
def test_outbound_document_url(page):
    # Initialize pages
    login_page = LoginPage(page)
    dashboard_page = AgentDashboardPage(page)
    outbound_page = OutboundPage(page)
    
    # 1. Login
    login_page.navigate(Config.BASE_URL)
    login_page.login(Config.USERNAME, Config.PASSWORD)
    
    # Verify login success
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
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    contact_list_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(contact_list_path)
    
    # 5. Select Template (qa_documento_url) with URL
    pdf_url = Config.TestData.PDF_URL
    
    outbound_page.select_template("qa_documento_url", attachment_url=pdf_url)
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success handled by send_outbound

@pytest.mark.smoke
def test_outbound_image_url(page):
    # Initialize pages
    login_page = LoginPage(page)
    dashboard_page = AgentDashboardPage(page)
    outbound_page = OutboundPage(page)
    
    # 1. Login
    login_page.navigate(Config.BASE_URL)
    login_page.login(Config.USERNAME, Config.PASSWORD)
    
    # Verify login success
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
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    contact_list_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(contact_list_path)
    
    # 5. Select Template (qa_imagen_url) with URL
    image_url = Config.TestData.IMAGE_URL
    
    outbound_page.select_template("qa_imagen_url", attachment_url=image_url)
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success handled by send_outbound

@pytest.mark.smoke
def test_outbound_video_url(page):
    # Initialize pages
    login_page = LoginPage(page)
    dashboard_page = AgentDashboardPage(page)
    outbound_page = OutboundPage(page)
    
    # 1. Login
    login_page.navigate(Config.BASE_URL)
    login_page.login(Config.USERNAME, Config.PASSWORD)
    
    # Verify login success
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
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    contact_list_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(contact_list_path)
    
    # 5. Select Template (qa_video_url) with URL
    
    
    outbound_page.select_template("qa_video_url", attachment_url=video_url)
    video_url = Config.TestData.VIDEO_URL
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success handled by send_outbound


@pytest.mark.smoke
def test_outbound_qa_header_boton(page):
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
    file_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(file_path)
    
    # 5. Select Template
    outbound_page.select_template("qa_header_boton")
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success handled by send_outbound


@pytest.mark.smoke
def test_outbound_qa_asterisco_inicio(page):
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
    file_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(file_path)
    
    # 5. Select Template
    outbound_page.select_template("qa_asterisco_inicio")
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success handled by send_outbound


@pytest.mark.smoke
def test_outbound_qa_plantilla_portugues(page):
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
    file_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(file_path)
    
    # 5. Select Template
    outbound_page.select_template("qa_plantilla_portugues")
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success handled by send_outbound


@pytest.mark.smoke
def test_outbound_qa_plantila_ingles(page):
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
    file_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(file_path)
    
    # 5. Select Template
    outbound_page.select_template("qa_plantila_ingles")
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success handled by send_outbound


@pytest.mark.smoke
def test_outbound_qa_boton_llamar(page):
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
    file_path = os.path.join(base_dir, "utils", "Plantilla_HSM.xlsx")
    
    outbound_page.upload_contact_list(file_path)
    
    # 5. Select Template
    outbound_page.select_template("qa_boton_llamar")
    
    # 6. Select Agent (Yo)
    outbound_page.select_agent("Yo")
    
    # 7. Send Outbound
    outbound_page.send_outbound()
    
    # Verify success handled by send_outbound