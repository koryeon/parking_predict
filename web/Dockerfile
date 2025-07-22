FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# .env 파일 포함 (로컬 개발용 환경변수)
COPY .env /app/.env

# 애플리케이션 코드 복사
COPY . .

# 정적 파일 수집을 위해 환경변수 설정
ENV DJANGO_SETTINGS_MODULE=park_pjt.settings

# 정적 파일 수집
RUN python manage.py collectstatic --noinput

# 마이그레이션 실행
RUN python manage.py migrate

EXPOSE 8000

# Application Insights 연동은 애플리케이션 내에서 설정됨
CMD ["gunicorn", "park_pjt.wsgi:application", "--bind", "0.0.0.0:8000"]