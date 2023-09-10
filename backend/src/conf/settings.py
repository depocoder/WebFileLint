import os
from pathlib import Path

from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists

if env.bool("BUILD", False):
    SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD = "build", 1234, "build", "build"
    SECRET_KEY = "build"
else:
    SECRET_KEY = env("SECRET_KEY")
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = env.int("SMTP_PORT")
    SMTP_USERNAME = env("SMTP_USERNAME")
    SMTP_PASSWORD = env("SMTP_PASSWORD")

DEFAULT_MESSAGE = (
    "Здравствуйте, ваш файл {file_name} был проверен, пожалуйста зайдите на сайт\n\n С уважением администрация "
    "LintChecker.ru"
)
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = env.bool("DEBUG", True)

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "checker",
    "drf_yasg",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

ROOT_URLCONF = "conf.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "checker/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "conf.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.postgresql_psycopg2"),
        "NAME": os.environ.get("DB_NAME", "lint_checker"),
        "USER": os.environ.get("POSTGRES_USER", "lint_checker"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "lint_checker"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = ()

AMQP_HOST = env("AMQP_HOST", "rabbitmq_server")
AMQP_PORT = env("AMQP_PORT", "5672")
MAIL_QUEUE = "mail_notififcation_queue"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "media/"
