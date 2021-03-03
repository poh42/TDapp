import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mailchimp_transactional as MailchimpTransactional
import os
from typing import List
import logging

log = logging.getLogger(__name__)

if not os.getenv("MAILCHIMP_API_KEY"):
    print("Warning: MAILCHIMP_API_KEY is not specified")


def send_email(to: List[str], subject: str, text: str, html: str) -> bool:
    to_list = []
    for email in to:
        to_list.append({"type": "to", "email": email})

    client = MailchimpTransactional.Client(os.getenv("MAILCHIMP_API_KEY"))
    try:
        response = client.messages.send(
            {
                "message": {
                    "html": html,
                    "text": text,
                    "from_email": "noreply@playtopdog.com",
                    "from_name": "Support",
                    "to": to_list,
                    "subject": subject,
                }
            }
        )
        log.debug(response)
        print("Email sent!")
        return True
    except Exception as e:
        log.error(e)
        print(f"There was an error sending email {str(e)}")
        return False
