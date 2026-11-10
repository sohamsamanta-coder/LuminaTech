
"""
Django settings for the LuminaTech project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# ================= BASE DIRECTORY =================

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the project root .env file
load_dotenv(BASE_DIR / ".env")


# ================= SECURITY SETTINGS =================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "DJANGO_SECRET_KEY is missing from environment variables."
    )

DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in (
    "true", "1", "yes"
)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "DJANGO_CSRF_TRUSTED_ORIGINS", ""
    ).split(",")
    if origin.strip()
]


# ================= GEMINI AI CONFIGURATION =================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ================= INSTALLED APPLICATIONS =================

INSTALLED_APPS = [
    "Ltfront",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]


# ================= MIDDLEWARE =================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ================= PROJECT CONFIGURATION =================

ROOT_URLCONF = "LuminaTech.urls"

WSGI_APPLICATION = "LuminaTech.wsgi.application"


# ================= TEMPLATES =================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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


# ================= DATABASE =================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ================= PASSWORD VALIDATION =================

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


# ================= LANGUAGE AND TIME =================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ================= STATIC FILES =================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# ================= MEDIA FILES =================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ================= EMAIL CONFIGURATION =================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")

EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))

EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in (
    "true", "1", "yes"
)

EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() in (
    "true", "1", "yes"
)

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER or ""
)

# Customer feedback goes to the official LuminaTech email.
FEEDBACK_RECEIVER_EMAIL = os.getenv(
    "FEEDBACK_RECEIVER_EMAIL",
    DEFAULT_FROM_EMAIL
)

EMAIL_TIMEOUT = 20


# ================= DEFAULT PRIMARY KEY =================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
