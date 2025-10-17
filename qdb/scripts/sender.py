import os
from smtplib import SMTP
from ssl import create_default_context
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .settings import (
    SMTP_SERVER,
    PORT,
    APP_IP,
    FROM_ADDRESS,
    PASSWORD,
    MESSAGE_CLOSER,
    ENV,
)


def get_message_body(
    month_name: str, year: int | str, unit: str, accounts: list[str]
) -> str:
    """Get the message body for the report.

    :param month_name: The name of the month
    :param year: The year
    :param unit: The name of the unit
    :param accounts: The accounts to include in the report
    :return: The message body
    """
    msg = "Please find attached the general ledger summary report for"
    msg += f" {month_name} {year} for {unit}, which covers the following accounts:"
    for acct in accounts:
        msg += f"\n{acct}"
    return msg + MESSAGE_CLOSER


def get_message_subject(month_name: str, year: int | str, unit: str) -> str:
    """Get the message subject for the report.

    :param month_name: The name of the month
    :param year: The year
    :param unit: The name of the unit
    :return: The message subject
    """
    return f"{month_name} {year} Financial Report: {unit}"


def send_report(data: dict, filename: str, recipients: list[str] | set[str]):
    """Send the report.

    :param data: The data to include in the report
    :param filename: The filename of the report
    :param recipients: The emails of recipients to send the report to
    """
    accts = [d["account"] for d in data["accounts"]]
    body = get_message_body(data["month_name"], data["year"], data["unit"], accts)

    message = MIMEMultipart()
    message["From"] = FROM_ADDRESS
    message["To"] = ", ".join(recipients)
    message["Subject"] = get_message_subject(
        data["month_name"], data["year"], data["unit"]
    )
    message.attach(MIMEText(body, "plain"))

    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition", f"attachment; filename={os.path.split(filename)[1]}"
    )

    message.attach(part)
    text = message.as_string()

    with SMTP(SMTP_SERVER, int(PORT), APP_IP) as server:
        # Local devs use gmail which requires smtp auth and tls.
        # Central test/prod environment uses ucla smtp: no auth/tls, ip-restricted.
        if ENV == "dev":
            server.ehlo()
            server.starttls(context=create_default_context())
            server.ehlo()
            server.login(FROM_ADDRESS, PASSWORD)
        server.sendmail(FROM_ADDRESS, list(recipients), text)
