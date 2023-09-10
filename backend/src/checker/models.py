from django.contrib.auth.models import User
from django.db import models


class File(models.Model):
    class StatusChoice(models.TextChoices):
        waiting = "waiting", "waiting"
        success = "success", "success"
        in_queue = "in queue", "in queue"
        fail = "fail", "fail"

    raw_file = models.FileField(upload_to="raw_uploads/")
    user = models.ForeignKey(User, related_name="files", on_delete=models.CASCADE)

    last_check = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, default=StatusChoice.waiting, choices=StatusChoice.choices)

    file_name = models.CharField(max_length=256, blank=True)
    is_deleted = models.BooleanField(default=False)


class LintFile(models.Model):
    class StatusChoice(models.TextChoices):
        waiting = "waiting", "waiting"
        success = "success", "success"
        in_queue = "in queue", "in queue"
        fail = "fail", "fail"

    class LinterChoice(models.TextChoices):
        flake8 = "flake8", "flake8"
        ruff = "ruff", "ruff"
        mypy = "mypy", "mypy"

    raw_file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="checks")
    linter_output = models.FileField(upload_to="linter_output/", default=None, blank=True, null=True)
    status = models.CharField(max_length=32, default=StatusChoice.waiting, choices=StatusChoice.choices)
    linter = models.CharField(max_length=32, default=LinterChoice.flake8, choices=LinterChoice.choices)
    mail_sent = models.DateTimeField(null=True, blank=True)
