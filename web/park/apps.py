from django.apps import AppConfig
import logging


class ParkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'park'

    def ready(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logger.info("로거 초기화 완료")  # 필요한 경우 메시지 대체