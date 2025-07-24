from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import pickle
import logging
import numpy as np

app = FastAPI()

logging.basicConfig(level=logging.INFO)

class PredictRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    weekday: int
    temp: float
    rain: float
    lat: float      # 위도 직접 받기
    lng: float      # 경도 직접 받기

# 모델 로딩
with open("lgbm_classifier.pkl", "rb") as f:
    clf_model = pickle.load(f)
with open("best_lgbm.pkl", "rb") as f:
    reg_model = pickle.load(f)
with open('kmeans_cluster_model.pkl', 'rb') as f:
    kmeans = pickle.load(f)
print("✅ 모든 모델 로딩 완료")

def predict_cluster(lat, lng):
    """위도, 경도를 받아서 클러스터 예측"""
    try:
        if lat is None or lng is None:
            return -1
        
        # 경도, 위도 순서로 kmeans 모델에 입력
        geo_point = np.array([[lng, lat]])  # [경도, 위도] 순서
        cluster = kmeans.predict(geo_point)[0]
        logging.info(f"📍 좌표 클러스터 예측: lat={lat}, lng={lng} -> cluster={cluster}")
        return int(cluster)
    except Exception as e:
        logging.error(f"❌ 클러스터 예측 오류: {e}")
        return -1

@app.post("/predict")
def predict(input_data PredictRequest):
    logging.info("▶ 요청 도착: 입력 데이터 수신 완료")
    try:
        # 위도, 경도로 클러스터 계산
        cluster = predict_cluster(input_data.lat, input_data.lng)
        logging.info(f"▶ 클러스터 계산 완료: {cluster}")
        
        # 모델 입력 데이터 준비 (cluster 포함)
        model_data = {
            "year": input_data.year,
            "month": input_data.month,
            "day": input_data.day,
            "hour": input_data.hour,
            "weekday": input_data.weekday,
            "temp": input_data.temp,
            "rain": input_data.rain,
            "cluster": cluster
        }
        
        X = pd.DataFrame([model_data])
        logging.info("▶ 데이터프레임 변환 완료")
        
        # 분류 모델 예측 (확률)
        prob = clf_model.predict_proba(X)[:, 1][0]
        logging.info(f"▶ 분류 모델 예측 완료: 확률={prob:.4f}")

        # 회귀 모델 예측 (원시값)
        raw_pred = reg_model.predict(X)[0]
        logging.info(f"▶ 회귀 모델 예측 완료: 원시값={raw_pred:.4f}")

        # 최종 기대값 계산
        expected = prob * raw_pred
        logging.info(f"▶ 최종 기대 민원 계산 완료: {expected:.4f}")

        return {
            "probability_percent": round(prob * 100, 2),
            "raw_prediction": round(raw_pred, 2),
            "expected_violations": round(expected, 2),
            "cluster_used": cluster  # 디버깅용
        }

    except Exception as e:
        logging.error(f"❌ 예외 발생: {e}")
        return {"error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "FastAPI AI 서버가 정상 동작 중입니다."}


