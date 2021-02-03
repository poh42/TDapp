import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from typing import List
import logging

log = logging.getLogger(__name__)


def send_email(to: List[str], subject: str, text: str, html: str) -> bool:
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    sent_from = email_user
    recipients = ", ".join(to)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sent_from
    msg['To'] = recipients

    plain_msg = MIMEText(text, 'plain')
    html_msg = MIMEText(html, 'html')

    msg.attach(plain_msg)
    msg.attach(html_msg)

    try:
        server = smtplib.SMTP(
            os.getenv("EMAIL_SMTP_SERVER"), os.getenv("EMAIL_SMTP_PORT")
        )
        server.connect(os.getenv("EMAIL_SMTP_SERVER"), os.getenv("EMAIL_SMTP_PORT"))
        server.ehlo()
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(sent_from, recipients, msg.as_string())
        server.close()

        print("Email sent!")
        return True
    except Exception as e:
        print("There was an error sending email", e)
        log.error(e)
        return False
