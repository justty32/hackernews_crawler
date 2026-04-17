import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from utils.config import get_env

def send_email(subject, body, email_cfg):
    """發送 Email 通知"""
    smtp_host = get_env("SMTP_HOST")
    smtp_port = int(get_env("SMTP_PORT", 587))
    smtp_user = get_env("SMTP_USERNAME")
    smtp_pass = get_env("SMTP_PASSWORD")
    recipient = email_cfg['recipient']
    
    if not all([smtp_host, smtp_user, smtp_pass]):
        print("SMTP settings incomplete. Skipping email.")
        return False
        
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = smtp_user
    msg['To'] = recipient
    
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [recipient], msg.as_string())
        server.quit()
        print(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def save_to_file(subject, body, output_dir):
    """將通知內容存入指定資料夾"""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Subject: {subject}\n")
        f.write("=" * 30 + "\n")
        f.write(body)
    print(f"Notification saved to folder: {filepath}")
