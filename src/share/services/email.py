from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

from fastapi import Depends

from config.settings import Settings, settings

logger = logging.getLogger(__name__)


class EmailService:
    host: Optional[str]
    port: int
    username: Optional[str]
    password: Optional[str]
    use_tls: bool
    from_email: Optional[str]
    from_name: str

    def __init__(self, cfg: Settings | None = None) -> None:
        cfg = cfg or settings
        self.host = cfg.SMTP_HOST
        self.port = cfg.SMTP_PORT
        self.username = cfg.SMTP_USERNAME
        self.password = cfg.SMTP_PASSWORD
        self.use_tls = cfg.SMTP_USE_TLS
        self.from_email = str(cfg.SMTP_FROM) if cfg.SMTP_FROM else None
        self.from_name = cfg.SMTP_FROM_NAME

    @classmethod
    def get_service(cls, cfg: Settings = Depends(lambda: settings)) -> "EmailService":
        return cls(cfg)

    def _build_message(
        self, *, message: str, to_email: str, subject: str
    ) -> EmailMessage:
        if not self.from_email:
            raise RuntimeError("SMTP_FROM must be configured to send emails")

        msg = EmailMessage()
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        body = message or ""
        is_html = (
            "<" in body
            and ">" in body
            and (
                "<html" in body.lower()
                or "<!doctype" in body.lower()
                or "<body" in body.lower()
            )
        )
        if is_html:
            text_fallback = "This email contains HTML content. Please view it in an HTML-compatible email client."
            msg.set_content(text_fallback)
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)
        return msg

    def send_email(self, message: str, to_email: str, subject: str) -> None:
        if not self.host or not self.port:
            raise RuntimeError("SMTP_HOST/SMTP_PORT must be configured to send emails")

        email = self._build_message(message=message, to_email=to_email, subject=subject)

        logger.info(
            "Sending email: to=%s host=%s port=%s tls=%s",
            to_email,
            self.host,
            self.port,
            self.use_tls,
        )

        if self.use_tls:
            with smtplib.SMTP(self.host, self.port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(email)
        else:
            with smtplib.SMTP_SSL(self.host, self.port) as server:
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(email)

        logger.info("Email sent successfully to=%s", to_email)
