import json
import logging
import socket
import smtplib
import subprocess
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import uuid4

import pika
from django.conf import settings
from django.utils import timezone

from checker.models import File, LintFile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lint_check(lint_file: LintFile, file: File):
    file_path = file.raw_file.path
    report_filename = f"{lint_file.pk}.{lint_file.linter}"
    with tempfile.NamedTemporaryFile("r") as tmp_file:
        command = f"{lint_file.linter} {file_path} > {tmp_file.name}"
        process = subprocess.Popen(command, shell=True)
        process.wait()

        file.last_check = timezone.now()
        file.status = File.StatusChoice.success

        lint_file.status = LintFile.StatusChoice.success
        lint_file.linter_output.save(report_filename, tmp_file, save=False)
        logger.info(f"File has been succesfully checked {file=} {lint_file=}")


def prepare_rabbitmq_message(task_name, *args):
    body = {"id": str(uuid4), "task": task_name, "args": args}
    return json.dumps(body)


def send_message_in_rabbitmq(message, routing_key):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.AMQP_HOST, port=settings.AMQP_PORT)
        )
        channel = connection.channel()

        channel.basic_publish(
            exchange="",
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(content_type="application/json"),
        )

    finally:
        connection.close()


def send_email(customer_email, subject, message):
    socket.setdefaulttimeout(120)
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USERNAME
    msg["To"] = customer_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))
    try:
        smtp = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        if settings.DEBUG:
            smtp.set_debuglevel(1)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(msg)
    finally:
        smtp.quit()
