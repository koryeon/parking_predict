from pathlib import Path
import os
from dotenv import load_dotenv
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
load_dotenv()

logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"))
)


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-@i!##57i$+5$-w_&4+1-mjjo_xcci8e@ea54^n73!-2nx0b%_w'

DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'parkingpredict.store', 'www.parkingpredict.store', '20.249.170.4']

CSRF_TRUSTED_ORIGINS = [
    'https://parkingpredict.store',
    'https://www.parkingpredict.store'
]

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
KAKAO_REST_API_JS_KEY = os.getenv("KAKAO_REST_API_JS_KEY")

# ✅ Application Insights 연결 문자열 (Azure Portal에서 확인)
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

INSTALLED_APPS = [
    'park',
    'map',
    'schedule',
    'accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.naver',

    # ✅ Application Insights용
    'opencensus.ext.django',
]

SITE_ID = 2

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_LOGOUT_ON_GET = True

LOGIN_REDIRECT_URL = '/park/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # ✅ Application Insights 미들웨어 추가
    'opencensus.ext.django.middleware.OpencensusMiddleware',
]

ROOT_URLCONF = 'park_pjt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'park_pjt.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'web' / 'static']
STATIC_ROOT = BASE_DIR / 'web' / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

APPEND_SLASH = True
# ✅ 배포 환경에서 꼭 있어야 할 설정
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 3600

# ✅ OpenCensus 설정 (Application Insights)
OPENCENSUS = {
    'TRACE': {
        'EXPORTER': 'opencensus.ext.azure.trace_exporter.AzureExporter',
        'EXPORTER_ARGS': {
            'connection_string': APPLICATIONINSIGHTS_CONNECTION_STRING,
        },
        'SAMPLER': 'opencensus.trace.samplers.ProbabilitySampler',
        'SAMPLER_ARGS': {
            'probability': 1.0,
        },
    }
}