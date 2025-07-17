from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-@i!##57i$+5$-w_&4+1-mjjo_xcci8e@ea54^n73!-2nx0b%_w'

DEBUG = True  # 배포 시 반드시 False로 변경!

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'parkingpredict.store','www.parkingpredict.store', '20.249.162.204']

CSRF_TRUSTED_ORIGINS = [
    'https://parkingpredict.store',
    'https://www.parkingpredict.store'
]

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

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
]

SITE_ID = 2

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_LOGOUT_ON_GET = True  # 로그아웃 시 GET으로도 처리되게

# ✅ 로그인/로그아웃 관련 경로 설정
# ✅ 로그인 성공 후 이동할 기본 페이지 (로그인 후 실제 콘텐츠로 가야 함)
LOGIN_REDIRECT_URL = '/park/'  # 유지해도 OK

# ✅ 로그아웃 후 이동할 페이지를 명확하게 'login 페이지'로 지정
LOGOUT_REDIRECT_URL = '/accounts/login/'  # ✅ 여기가 최종 도착지

# ✅ allauth의 logout redirect도 위와 같이 login 페이지로 맞춰줌
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'  # 🔧 이걸 /accounts/logout/ 으로 두면 무한 루프 발생!

SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 브라우저 닫을 때 세션 만료

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'http')

APPEND_SLASH = True