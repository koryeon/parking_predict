from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.CharField(max_length=10, default="00")
    temp = models.FloatField(default=0)
    rain = models.FloatField(default=0)
    address = models.CharField(max_length=200, default="")      # 주소 필드 추가
    latitude = models.FloatField(null=True, blank=True)         # 위도 필드 추가
    longitude = models.FloatField(null=True, blank=True)        # 경도 필드 추가
    probability_percent = models.FloatField(default=0)
    raw_prediction = models.FloatField(default=0)
    expected_violations = models.FloatField(default=0)


    def __str__(self):
        return f"{self.user.username} - {self.date} {self.time}"
