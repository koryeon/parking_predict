import requests
from schedule.models import Prediction
from django.shortcuts import render, redirect
from datetime import datetime
from geopy.geocoders import Nominatim

from geopy.geocoders import Nominatim
import urllib.parse

def geocoding(address):
    print(f"🔍 [DEBUG] geocoding 시작 - 입력 주소: {address}")
    
    # 한국어 주소를 URL 인코딩
    encoded_address = urllib.parse.quote(address, safe='')
    print(f"🔍 [DEBUG] URL 인코딩된 주소: {encoded_address}")
    
    # user_agent에 한국어 문자 제거
    geolocator = Nominatim(user_agent='parking_prediction_app', timeout=10)
    
    try:
        # 원본 주소로 시도
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
        # 대안: 간단한 주소로 재시도
        try:
            simple_address = address.replace('아차산로 200', '').strip()
            print(f"🔍 [DEBUG] 간단한 주소로 재시도: {simple_address}")
            location = geolocator.geocode(simple_address, language='ko')
            
            if location:
                result = {
                    "lat": location.latitude,
                    "lng": location.longitude,
                    "full_address": location.address
                }
                print(f"✅ [DEBUG] 간단한 주소로 geocoding 성공: {result}")
                return result
        except Exception as e2:
            print(f"❌ [DEBUG] 간단한 주소로도 실패: {e2}")
        
        return None


def parse_date_and_weekday(date_str):
    print(f"🔍 [DEBUG] parse_date_and_weekday 시작 - 입력 날짜: {date_str}")
    # '2025-08-13' → (2025, 8, 13, 2) (화요일)
    year, month, day = map(int, date_str.split('-'))
    date_obj = datetime(year, month, day)
    weekday = date_obj.weekday()  # 월=0, 일=6
    print(f"✅ [DEBUG] 날짜 파싱 결과: year={year}, month={month}, day={day}, weekday={weekday}")
    return year, month, day, weekday

def park(request):
    print(f"🔍 [DEBUG] park 뷰 시작 - 요청 방식: {request.method}")
    context = {}

    if request.method == 'POST':
        print(f"🔍 [DEBUG] POST 요청 데이터: {dict(request.POST)}")
        
        date_input = request.POST.get('day', '')      # yyyy-mm-dd
        hour_input = request.POST.get('hour', '0')    # '0'~'23'
        temp = request.POST.get('temp', '')
        rain = request.POST.get('rain', '')
        address = request.POST.get('address', '')     # 클러스터 대신 주소 입력

        print(f"📝 [DEBUG] 폼 입력값들:")
        print(f"  - date_input: {date_input}")
        print(f"  - hour_input: {hour_input}")
        print(f"  - temp: {temp}")
        print(f"  - rain: {rain}")
        print(f"  - address: {address}")

        # 날짜 파싱 및 weekday 계산
        try:
            year, month, day, weekday = parse_date_and_weekday(date_input)
        except Exception as e:
            print(f"❌ [DEBUG] 날짜 파싱 실패: {e}")
            year, month, day, weekday = 2025, 1, 1, 0  # 기본값

        # 시간 변환
        try:
            hour = int(hour_input)
            if hour < 0 or hour > 23:
                hour = 0
            print(f"✅ [DEBUG] 시간 변환 성공: {hour}")
        except Exception as e:
            print(f"❌ [DEBUG] 시간 변환 실패: {e}")
            hour = 0

        # 주소를 좌표로 변환
        coordinates = None
        if address:
            print(f"🔍 [DEBUG] 주소 → 좌표 변환 시작")
            coordinates = geocoding(address)
            print(f"🔍 [DEBUG] 좌표 변환 결과: {coordinates}")
        else:
            print(f"⚠️ [DEBUG] 주소가 비어있음, 좌표 변환 생략")

        # 예측 버튼
        if 'predict' in request.POST:
            print(f"🔍 [DEBUG] 예측 버튼 클릭됨")
            try:
                # 좌표가 있으면 좌표 사용, 없으면 기본값 사용
                if coordinates:
                    lat = coordinates["lat"]
                    lng = coordinates["lng"]
                    print(f"✅ [DEBUG] 입력 주소 좌표 사용: lat={lat}, lng={lng}")
                else:
                    lat = 37.2636  # 수원시 기본 좌표
                    lng = 127.0286
                    print(f"⚠️ [DEBUG] 기본 좌표 사용: lat={lat}, lng={lng}")

                api_payload = {
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "weekday": weekday,        # 자동 계산
                    "temp": float(temp),       # 사용자 입력
                    "rain": float(rain),       # 사용자 입력
                    "lat": lat,                # 좌표 latitude
                    "lng": lng                 # 좌표 longitude
                }
                print(f"📤 [DEBUG] API 페이로드: {api_payload}")
                
            except Exception as e:
                print(f"❌ [DEBUG] API 페이로드 생성 실패: {e}")
                context['error'] = f"입력값 변환 오류: {e}"
                # 입력값들도 그대로 전송하여 폼에 보여줌
                context.update({
                    'result_date': date_input,
                    'result_time': hour_input,
                    'temp': temp,
                    'rain': rain,
                    'address': address,
                    'coordinates': coordinates,
                })
                print(f"📤 [DEBUG] 에러 context: {context}")
                return render(request, 'park/park.html', context)

            # API 호출 없이 더미 결과 생성 (실제 환경에서는 FastAPI 호출)
            ai_result = {
                "probability_percent": 85.5,
                "raw_prediction": 1.25,
                "expected_violations": 1.25
            }
            print(f"🤖 [DEBUG] AI 결과 (더미): {ai_result}")

            # 입력값들도 context에 추가
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
            print(f"📤 [DEBUG] 최종 context: {context}")
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
