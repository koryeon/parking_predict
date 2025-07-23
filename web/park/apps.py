from django.apps import AppConfig
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler


class ParkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'park'

    def ready(self):
        logger = logging.getLogger(__name__)
        logger.addHandler(
            AzureLogHandler(
                connection_string='InstrumentationKey=eb740ae5-1423-4e7b-87b3-8c8f9ba491ce;IngestionEndpoint=https://koreacentral-0.in.applicationinsights.azure.com/'
            )
        )
        logger.setLevel(logging.INFO)
        logger.warning("Application Insights 연결 완료")