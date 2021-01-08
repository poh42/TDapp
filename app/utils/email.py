import smtplib
import os
from typing import List
import logging

log = logging.getLogger(__name__)


def send_email(to: List[str], subject: str, text: str, html: str) -> bool:
    # TODO this should support html messages
    # Check https://stackoverflow.com/questions/882712/sending-html-email-using-python
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    sent_from = email_user
    email_text = """\
From: %s
To: %s
Subject: %s

    %s
    """ % (
        sent_from,
        ", ".join(to),
        subject,
        text,
    )

    try:
        server = smtplib.SMTP_SSL(
            os.getenv("EMAIL_SMTP_SERVER"), os.getenv("EMAIL_SMTP_PORT")
        )
        server.ehlo()
        server.login(email_user, email_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print("Email sent!")
        return True
    except Exception as e:
        print("There was an error sending email", e)
        log.error(e)
        return False
