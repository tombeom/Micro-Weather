import os
import xml.etree.ElementTree as ET
from apps.utils import *
from datetime import datetime

async def getSunRiseSet(latitude, longitude):
    """
    한국천문연구원 OPEN API를 사용해 위경도 데이터를 바탕으로 현재 위치의 일출, 일몰 데이터를 조회하는 함수
    Args:
        latitude (str) : 위도
        longitude (str) : 경도
    """
    url = "http://apis.data.go.kr/B090041/openapi/service/RiseSetInfoService/getLCRiseSetInfo"
    params = {
        "serviceKey" : os.getenv("openAPIKey"),
        "locdate" : getDate(),
        "latitude" : latitude,
        "longitude" : longitude,
        "dnYn" : "Y"
    }

    try: # API 호출 시도 (GET Request)
        async with ClientSession() as session:
            async with session.get(url, params=params) as response:
                response = (await response.text())
                root = ET.fromstring(response)
    except Exception as e: # API 호출 실패
        return "ERROR"
    else: # API 호출 성공
        try: # API 호출 성공 후 데이터 처리
            if root[0][0].text == "00": # API 응답코드 확인
                sunriseText = (datetime.today().strftime("%Y%m%d")) + (root[1][0][0][15].text.strip())
                sunsetText = (datetime.today().strftime("%Y%m%d")) + (root[1][0][0][16].text.strip())
                nowTimeText = (datetime.today().strftime("%Y%m%d")) + (getTime().strip())

                sunrise = datetime.strptime(sunriseText, "%Y%m%d%H%M")
                sunset = datetime.strptime(sunsetText, "%Y%m%d%H%M")
                nowTime = datetime.strptime(nowTimeText, "%Y%m%d%H%M")

                if (nowTime > sunrise and nowTime < sunset):
                    return {"sunRiseSetData": "sunrise"}
                else:
                    return {"sunRiseSetData": "sunset"}
            else: raise Exception(f'getSunRiseSet() 비정상 응답 코드 : {root[0][0].text}') # API 응답코드가 비정상일 경우 에러 발생
        except Exception as e: # API 데이터 처리 실패
            return "ERROR"