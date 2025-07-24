import requests
from schedule.models import Prediction
from django.shortcuts import render, redirect
from datetime import datetime
from geopy.geocoders import Nominatim
import urllib.parse
from django.conf import settings

# FastAPI 서버 URL 설정
FASTAPI_BASE_URL = getattr(settings, 'FASTAPI_BASE_URL', 'http://parkapp2ai-service:8001')

def geocoding(address):
    """주소를 좌표로 변환하는 함수 (Django에서만 필요)"""
    print(f"🔍 [DEBUG] geocoding 시작 - 입력 주소: {address}")
    
    encoded_address = urllib.parse.quote(address, safe='')
    print(f"🔍 [DEBUG] URL 인코딩된 주소: {encoded_address}")
    
    geolocator = Nominatim(user_agent='parking_prediction_app', timeout=10)
    
    try:
        location = geolocator.geocode(address, language='ko')
        
        if location:
            result = {
                "lat": location.latitude,
                "lng": location.longitude,
                "full_address": location.address
            }
            print(f"✅ [DEBUG] geocoding 성공: {result}")
            return result
        else:
            print(f"❌ [DEBUG] geocoding 실패: 주소를 찾을 수 없음")
            return None
            
    except Exception as e:
        print(f"❌ [DEBUG] geocoding 예외 발생: {e}")
        return None

def call_fastapi_predict(api_payload):
    """FastAPI 서버 호출 함수 (Django에서 필요)"""
    try:
        url = f"{FASTAPI_BASE_URL}/predict"
        print(f"🌐 [DEBUG] FastAPI 호출 - URL: {url}")
        print(f"📤 [DEBUG] 전송 데이터: {api_payload}")
        
        response = requests.post(
            url,
            json=api_payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 [DEBUG] HTTP 응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ [DEBUG] FastAPI 호출 성공: {result}")
            return result, None
        else:
            error_msg = f"FastAPI 서버 오류: HTTP {response.status_code} - {response.text}"
            print(f"❌ [DEBUG] {error_msg}")
            return None, error_msg
            
    except requests.exceptions.ConnectionError:
        error_msg = f"FastAPI 서버 연결 실패: {FASTAPI_BASE_URL}"
        print(f"❌ [DEBUG] {error_msg}")
        return None, error_msg
        
    except Exception as e:
        error_msg = f"FastAPI 호출 중 예외: {str(e)}"
        print(f"❌ [DEBUG] {error_msg}")
        return None, error_msg

def parse_date_and_weekday(date_str):
    print(f"🔍 [DEBUG] 날짜 파싱: {date_str}")
    year, month, day = map(int, date_str.split('-'))
    date_obj = datetime(year, month, day)
    weekday = date_obj.weekday()
    print(f"✅ [DEBUG] 결과: year={year}, month={month}, day={day}, weekday={weekday}")
    return year, month, day, weekday

def park(request):
    print(f"🔍 [DEBUG] park 뷰 시작 - 요청: {request.method}")
    context = {}

    if request.method == 'POST':
        print(f"🔍 [DEBUG] POST 데이터: {dict(request.POST)}")
        
        # 폼 데이터 추출
        date_input = request.POST.get('day', '')
        hour_input = request.POST.get('hour', '0')
        temp = request.POST.get('temp', '')
        rain = request.POST.get('rain', '')
        address = request.POST.get('address', '')

        print(f"📝 [DEBUG] 입력값: date={date_input}, hour={hour_input}, temp={temp}, rain={rain}, address={address}")

        # 날짜 파싱
        try:
            year, month, day, weekday = parse_date_and_weekday(date_input)
        except Exception as e:
            print(f"❌ [DEBUG] 날짜 파싱 실패: {e}")
            year, month, day, weekday = 2025, 1, 1, 0

        # 시간 변환
        try:
            hour = int(hour_input)
            if not 0 <= hour <= 23:
                hour = 0
        except:
            hour = 0

        # 주소 → 좌표 변환
        coordinates = geocoding(address) if address else None

        # 예측 버튼 클릭
        if 'predict' in request.POST:
            print(f"🔍 [DEBUG] 예측 버튼 클릭")
            
            try:
                # 좌표 설정 (입력된 주소 or 기본값)
                if coordinates:
                    lat, lng = coordinates["lat"], coordinates["lng"]
                    print(f"✅ [DEBUG] 주소 좌표 사용: lat={lat}, lng={lng}")
                else:
                    lat, lng = 37.2636, 127.0286  # 수원시 기본 좌표
                    print(f"⚠️ [DEBUG] 기본 좌표 사용: lat={lat}, lng={lng}")

                # FastAPI에 전송할 데이터 (좌표 포함, 클러스터는 FastAPI에서 계산)
                api_payload = {
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "weekday": weekday,
                    "temp": float(temp),
                    "rain": float(rain),
                    "lat": lat,    # 위도만 전송
                    "lng": lng     # 경도만 전송
                }
                print(f"📤 [DEBUG] FastAPI 전송 데이터: {api_payload}")
                
                # FastAPI 호출 (클러스터 계산부터 AI 예측까지 모든 처리)
                ai_result, error = call_fastapi_predict(api_payload)
                
                if error:
                    context['error'] = f"AI 서버 오류: {error}"
                    context.update({
                        'result_date': date_input,
                        'result_time': hour_input,
                        'temp': temp,
                        'rain': rain,
                        'address': address,
                        'coordinates': coordinates,
                    })
                    return render(request, 'park/park.html', context)
                
                print(f"🤖 [DEBUG] AI 예측 결과: {ai_result}")
                
            except Exception as e:
                print(f"❌ [DEBUG] 예측 처리 실패: {e}")
                context['error'] = f"예측 처리 오류: {e}"
                context.update({
                    'result_date': date_input,
                    'result_time': hour_input,
                    'temp': temp,
                    'rain': rain,
                    'address': address,
                    'coordinates': coordinates,
                })
                return render(request, 'park/park.html', context)

            # 성공 시 결과 표시
            context.update({
                'result_date': date_input,
                'result_time': str(hour),
                'temp': temp,
                'rain': rain,
                'address': address,
                'coordinates': coordinates,
                'ai_result': ai_result,
                'show_save': True,
            })
            return render(request, 'park/park.html', context)

        # 저장 버튼 클릭 시
        if 'save' in request.POST:
            print(f"🔍 [DEBUG] 저장 버튼 클릭됨")
            print(f"🔍 [DEBUG] 사용자 인증 상태: {request.user.is_authenticated}")
            
            if not request.user.is_authenticated:
                print(f"❌ [DEBUG] 로그인되지 않음 - 로그인 페이지로 리디렉션")
                return redirect('account_login')

            # 저장할 값들
            date_input = request.POST.get('day', '')
            hour_input = request.POST.get('hour', '0')
            temp = request.POST.get('temp', '')
            rain = request.POST.get('rain', '')
            address = request.POST.get('address', '')
            prob = request.POST.get('probability_percent', '')
            raw_pred = request.POST.get('raw_prediction', '')
            expected = request.POST.get('expected_violations', '')

            print(f"📝 [DEBUG] 저장할 값들:")
            print(f"  - date_input: {date_input}")
            print(f"  - hour_input: {hour_input}")
            print(f"  - temp: {temp}")
            print(f"  - rain: {rain}")
            print(f"  - address: {address}")
            print(f"  - prob: {prob}")
            print(f"  - raw_pred: {raw_pred}")
            print(f"  - expected: {expected}")

            # 주소를 좌표로 변환해서 저장
            print(f"🔍 [DEBUG] 저장용 좌표 변환 시작")
            coordinates = geocoding(address) if address else None
            lat = coordinates["lat"] if coordinates else None
            lng = coordinates["lng"] if coordinates else None
            print(f"🔍 [DEBUG] 저장용 좌표: lat={lat}, lng={lng}")

            try:
                # Prediction 모델에 저장
                prediction = Prediction.objects.create(
                    user=request.user,
                    date=date_input,
                    time=hour_input,
                    temp=temp,
                    rain=rain,
                    address=address,           # 주소 저장
                    latitude=lat,              # 위도 저장
                    longitude=lng,             # 경도 저장
                    probability_percent=prob,
                    raw_prediction=raw_pred,
                    expected_violations=expected
                )
                print(f"✅ [DEBUG] 데이터베이스 저장 성공: {prediction.id}")
                print(f"🔍 [DEBUG] 저장된 데이터: {prediction}")
                
            except Exception as e:
                print(f"❌ [DEBUG] 데이터베이스 저장 실패: {e}")
                context['error'] = f"저장 중 오류 발생: {e}"
                return render(request, 'park/park.html', context)
            
            print(f"🔍 [DEBUG] 달력 페이지로 리디렉션")
            return redirect('schedule:schedule')

    print(f"🔍 [DEBUG] GET 요청 또는 일반 렌더링")
    return render(request, 'park/park.html')
