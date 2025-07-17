from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import pickle
import logging

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
    cluster: int

with open("lgbm_classifier.pkl", "rb") as f:
    clf_model = pickle.load(f)
with open("best_lgbm.pkl", "rb") as f:
    reg_model = pickle.load(f)
with open('kmeans_cluster_model.pkl', 'rb') as f:
    kmeans = pickle.load(f)
print("✅ 클러스터 모델 로딩 완료")

def predict_cluster(geo_point):
    try:
        if (not isinstance(geo_point, (list, tuple)) or
            len(geo_point) != 2 or
            geo_point[0] is None or geo_point[1] is None):
            return -1

        lon_lat = np.array(geo_point).reshape(1, -1)
        cluster = kmeans.predict(lon_lat)[0]
        return int(cluster)
    except Exception as e:
        print(f"클러스터 예측 오류: {e}")
        return -1
    
@app.post("/predict")
def predict(input_data: PredictRequest):
    logging.info("▶ 요청 도착: 입력 데이터 수신 완료")
    try:
        X = pd.DataFrame([input_data.dict()])
        logging.info("▶ 데이터프레임 변환 완료")
        
        prob = clf_model.predict_proba(X)[:, 1][0]
        logging.info(f"▶ 분류 모델 예측 완료: 확률={prob:.4f}")

        raw_pred = reg_model.predict(X)[0]
        logging.info(f"▶ 회귀 모델 예측 완료: 원시값={raw_pred:.4f}")

        expected = prob * raw_pred
        logging.info(f"▶ 최종 기대 민원 계산 완료: {expected:.4f}")

        return {
            "probability_percent": round(prob * 100, 2),
            "raw_prediction": round(raw_pred, 2),
            "expected_violations": round(expected, 2)
        }

    except Exception as e:
        logging.error(f"❌ 예외 발생: {e}")
        return {"error": str(e)}
