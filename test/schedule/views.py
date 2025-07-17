# schedule/views.py
import json
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from .models import Prediction
from django.shortcuts import render


@login_required
def schedule(request):
    predictions = Prediction.objects.filter(user=request.user)
    predictions_by_date = {}
    for p in predictions:
        d = p.date.strftime('%Y-%m-%d')
        if d not in predictions_by_date:
            predictions_by_date[d] = []
        predictions_by_date[d].append({
            "time": p.time,
            "temp": p.temp,
            "rain": p.rain,
            "address": p.address,                    # 클러스터 대신 주소
            "latitude": p.latitude,                  # 위도 추가
            "longitude": p.longitude,                # 경도 추가
            "probability_percent": p.probability_percent,
            "raw_prediction": p.raw_prediction,
            "expected_violations": p.expected_violations,
        })
    context = {
        "predictions_by_date_json": mark_safe(json.dumps(predictions_by_date)),
    }
    return render(request, "schedule/schedule.html", context)
