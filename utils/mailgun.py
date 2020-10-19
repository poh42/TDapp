from typing import List
from requests import Response, post
import os


class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    @classmethod
    def send_email(
        cls, email: List[str], subject: str, text: str, html: str
    ) -> Response:
        MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
        MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
        FROM_EMAIL = os.environ.get("MAILGUN_FROM_EMAIL")
        FROM_TITLE = os.environ.get("MAILGUN_FROM_TITLE")

        if MAILGUN_DOMAIN is None:
            raise MailgunException("No mailgun domain specified")
        if MAILGUN_API_KEY is None:
            raise MailgunException("Failed to load mailgun API key")
        if FROM_EMAIL is None:
            raise MailgunException("Failed to load mailgun from email address")
        if FROM_TITLE is None:
            raise MailgunException("Failed to load FROM_TITLE value")
        response = post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"{FROM_TITLE} <{FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html,
            },
            timeout=5,
        )
        if response.status_code != 200:
            raise MailgunException("Error sending email")
        return response
