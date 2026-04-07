from __future__ import annotations

import random
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


class EmailSender:
    """Builds and sends personalised birthday emails via SMTP."""

    def __init__(
        self,
        sender_email: str,
        app_password: str,
        templates_dir: Path,
        smtp_host: str,
        smtp_port: int,
        dry_run: bool = False,
    ) -> None:
        self._sender = sender_email
        self._password = app_password
        self._templates_dir = templates_dir
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._dry_run = dry_run

    def pick_template(self, name: str) -> str:
        """Choose a random letter template and substitute [NAME].

        Args:
            name: The recipient's name.

        Returns:
            The rendered template body as a string.

        Raises:
            FileNotFoundError: if no letter_*.txt files are found.
        """
        templates = list(self._templates_dir.glob("letter_*.txt"))
        if not templates:
            raise FileNotFoundError(
                f"No templates found in {self._templates_dir}. "
                "Add files named letter_1.txt, letter_2.txt, etc."
            )
        chosen = random.choice(templates)
        return chosen.read_text(encoding="utf-8").replace("[NAME]", name)

    def build_message(self, to_addr: str, subject: str, body: str) -> EmailMessage:
        """Construct an EmailMessage object.

        Args:
            to_addr: Recipient email address.
            subject: Email subject line.
            body: Plain-text email body.

        Returns:
            A ready-to-send EmailMessage.
        """
        msg = EmailMessage()
        msg["From"] = self._sender
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.set_content(body)
        return msg

    def send(self, msg: EmailMessage) -> None:
        """Send an EmailMessage via SMTP with STARTTLS.

        In dry_run mode, prints the message instead of sending.

        Raises:
            smtplib.SMTPException: on any SMTP-level failure.
        """
        if self._dry_run:
            print("\n--- DRY RUN ---")
            print("From:", msg["From"])
            print("To:", msg["To"])
            print("Subject:", msg["Subject"])
            print(msg.get_content())
            print("--- END ---")
            return

        context = ssl.create_default_context()
        with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
            server.starttls(context=context)
            server.login(self._sender, self._password)
            server.send_message(msg)
