from django.shortcuts import render
import requests
import xml.etree.ElementTree as ET
import math
import os
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 로드

SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 지구 반지름 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c  # km 단위 거리 반환

def get_latlng(address, KAKAO_REST_API_KEY):
    url = 'https://dapi.kakao.com/v2/local/search/address.json'
    headers = {
    "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}",
    "KA": "python/1.0 myapp os/Mac-14.5 origin/localhost"
    }
    params = {'query': address}
    res = requests.get(url, headers=headers, params=params)
    result = res.json()
    # 상세 디버깅 로그 추가
    #print(f"요청 주소: {address}")
    #print(f"응답 상태코드: {res.status_code}")
    #print(f"응답 전체: {result}")
    
    # documents 키가 없을 때를 대비해 .get() 사용
    documents = result.get('documents', [])
    if documents:
        lat = documents[0]['y']
        lng = documents[0]['x']
        return lat, lng
    # 실패 원인 분석
    print(f"카카오 주소 변환 실패 - 주소: {address}")
    print(f"실패 응답: {result}")
    
    # 에러 타입 확인
    if 'error' in result:
        print(f"API 에러: {result['error']}")
    
    return None, None



def map(request):
    api_url = f"http://openapi.seoul.go.kr:8088/{SEOUL_API_KEY}/xml/GetParkingInfo/1/50/"
    
    response = requests.get(api_url)
    xml_data = response.text
    root = ET.fromstring(xml_data)
    parking_list = []
    failed_addresses = []  # 실패한 주소 목록
    for row in root.findall('row'):
        name = row.find('PKLT_NM').text
        addr = row.find('ADDR').text
        now_cnt = row.find('NOW_PRK_VHCL_CNT').text
        total_cnt = row.find('TPKCT').text
        lat, lng = get_latlng(addr, KAKAO_REST_API_KEY)
        if lat and lng:
            parking_list.append({
                'name': name,
                'addr': addr,
                'now_cnt': now_cnt,
                'total_cnt': total_cnt,
                'lat': lat,
                'lng': lng
            })
        else:
            # 실패한 주소 기록
            failed_addresses.append({
                'name': name,
                'addr': addr
            })
    # 실패한 주소 출력
    if failed_addresses:
        print(f"총 {len(failed_addresses)}개 주소 변환 실패:")
        for failed in failed_addresses:
            print(f"- {failed['name']}: {failed['addr']}")

    # GET 방식이면 거리 계산 생략, POST일 때만 실행
    my_lat = request.POST.get('my_lat')
    my_lng = request.POST.get('my_lng')
    if my_lat is not None and my_lng is not None:
        try:
            my_lat = float(my_lat)
            my_lng = float(my_lng)
            for park in parking_list:
                park['distance'] = haversine(my_lat, my_lng, float(park['lat']), float(park['lng']))
            parking_list.sort(key=lambda x: x['distance'])
        except (ValueError, TypeError):
            # 값이 잘못 들어온 경우 예외 처리
            pass
    context = {
        'parking_list': parking_list,
        'kakao_js_key': settings.KAKAO_REST_API_JS_KEY  # 여기서 올바른 환경 변수 사용
    }
    #print("카카오 JS 키:", settings.KAKAO_REST_API_JS_KEY) 
    return render(request, 'map/map.html', context)
