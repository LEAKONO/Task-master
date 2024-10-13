from flask_mail import Mail, Message
from flask import current_app
from email.utils import formataddr
import logging

mail = Mail()

def send_notification(to, subject, message, html_message=None):
    try:
        if not to or not subject or not message:
            raise ValueError("Recipient, subject, and message are required.")

        msg = Message(subject, recipients=[to])
        msg.sender = formataddr(("TASKMASTER", current_app.config["MAIL_DEFAULT_SENDER"]))

        msg.body = message
        if html_message:
            msg.html = html_message

        msg.reply_to = current_app.config["MAIL_DEFAULT_SENDER"]
        msg.headers = {
            "X-Priority": "1",
            "X-Mailer": "TASKMASTER",
            "Precedence": "bulk",
        }

        mail.send(msg)
        logging.info(f"Email sent to {to} with subject: {subject}")

    except Exception as e:
        logging.error(f"Failed to send email to {to}: {str(e)}")
