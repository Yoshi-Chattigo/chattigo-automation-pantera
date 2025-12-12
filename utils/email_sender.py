import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from utils.logger import get_logger

class EmailSender:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SMTP_SENDER")
        self.password = os.getenv("SMTP_PASSWORD")

    def send_email(self, subject: str, body: str, to_email: str):
        """
        Sends an email using the configured SMTP server.
        """
        if not self.sender_email or not self.password:
            self.logger.error("SMTP credentials not configured (SMTP_SENDER, SMTP_PASSWORD).")
            raise ValueError("SMTP credentials missing.")

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            self.logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            self.logger.info(f"Logging in as {self.sender_email}")
            server.login(self.sender_email, self.password)
            
            self.logger.info(f"Sending email to {to_email}")
            text = msg.as_string()
            server.sendmail(self.sender_email, to_email, text)
            
            server.quit()
            self.logger.info("Email sent successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            raise e
