import logging

from django.conf import settings
from django.utils import timezone

from checker.models import File, LintFile
from checker.utils import lint_check, send_email, send_message_in_rabbitmq, prepare_rabbitmq_message
from conf.celery import app

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.task
def send_notification(email, lint_file_pk, file_name):
    logger.info(f"Starting send_notification to {email}")
    lint_file = LintFile.objects.get(pk=lint_file_pk)
    send_email(
        email,
        "Ваш файл был проверен!",
        settings.DEFAULT_MESSAGE.format(
            file_name=file_name,
        ),
    )
    lint_file.mail_sent = timezone.now()
    lint_file.save()
    logger.info(f"Mail sent to {email}")


@app.task
def regular_checking():
    LintFile.objects.filter(status=LintFile.StatusChoice.waiting).update(status=LintFile.StatusChoice.in_queue)
    lint_files = LintFile.objects.filter(status=LintFile.StatusChoice.in_queue).select_related("raw_file")
    for lint_file in lint_files:
        file = lint_file.raw_file
        try:
            lint_check(lint_file, file)
            message = prepare_rabbitmq_message(
                "checker.tasks.send_notification",
                *(file.user.email, lint_file.pk, file.file_name)
            )
            send_message_in_rabbitmq(message, settings.MAIL_QUEUE)
        except:
            file.status = File.StatusChoice.fail
            file.last_check = timezone.now()
            lint_check.status = LintFile.StatusChoice.fail
            logger.error(f"Can't check file {file} {lint_file}", exc_info=True)
        finally:
            lint_file.save()
            file.save()
