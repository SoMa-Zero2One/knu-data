import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pathlib import Path
import logging

load_dotenv()

logger = logging.getLogger("email")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def send_email (to_address : str, nickname : str, uuid : str, college_name : str) :
    
    logger.debug(f"[Send Email] : {to_address}")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    with open(DATA_DIR / "email_title.txt", encoding = "utf-8") as f :
        subject = f.read()
    
    with open(DATA_DIR / "email_content_template.txt", encoding = "utf-8") as f :
        body = f.read().format(nickname = nickname, uuid = uuid)

    msg = MIMEText(body)
    msg["From"]     = smtp_user
    msg["To"]       = to_address
    msg["Subject"]  = subject

    with smtplib.SMTP(smtp_host, smtp_port) as smtp :
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)
        
    logger.debug(f"[Sent Email] : {to_address}")
    