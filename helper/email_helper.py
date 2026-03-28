


from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv
from pathlib import Path


# SMTP_SERVER="smtp.gmail.com"
# SMTP_PORT=587
# SMTP_EMAIL="rutu.pansaniya@seaflux.tech"
# SMTP_PASSWORD="smgkfncprcxtfayd"

SMTP_SERVER=os.getenv("SMTP_SERVER")
SMTP_PORT=os.getenv("SMTP_PORT")
SMTP_EMAIL=os.getenv("SMTP_EMAIL")
SMTP_PASSWORD=os.getenv("SMTP_PASSWORD")

# port = os.getenv("SMTP_PORT")

#
class EmailHelper:
    def send_otp_email(receiver_email: str, otp_code: str):
        msg = EmailMessage()
        msg.set_content(f"Your SeaBasket login verification code is: {otp_code}. It expires in 5 minutes.")
        msg['Subject'] = 'SeaBasket Verification'
        msg['From'] = SMTP_EMAIL # Your server email
        msg['To'] = receiver_email             # The user's email from DB

        try:
            with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
                server.starttls()
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"SMTP Error: {e}")
            return False