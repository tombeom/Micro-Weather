import requests
from apps.keys import openAPIKey
from apps.logger import setLogger
from apps.getDateTime import *

async def getNowcast(gridX, gridY):
    """
    기상청 OPEN API를 사용해 초단기실황 데이터를 조회하는 함수
    Args:
        gridX (str) : 기상청 Grid 좌표계 X 좌표
        gridY (str) : 기상청 Grid 좌표계 Y 좌표
    """
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    params = {
        "serviceKey" : openAPIKey,
        "numOfRows" : "30",
        "pageNo" : "1",
        "dataType" : "JSON",
        "base_date" : getDate("ncst"),
        "base_time" : getTime("ncst"),
        "nx" : gridX,
        "ny" : gridY
        }
    try: # API 호출 시도 (GET Request)
        response = requests.get(url, params=params, verify=False).json()
    except Exception as e: # API 호출 실패
        logger = setLogger("api", "getNowcastError")
        logger.error("getNowcast API 호출 오류")
        logger.error(e)
        return "ERROR"
    else: # API 호출 성공
        try: # API 호출 성공 후 데이터 처리
            if response["response"]["header"]["resultCode"] == "00": # API 응답코드 확인
                # 응답코드가 정상 값이면 데이터 return
                responseData = response["response"]["body"]["items"]["item"]

                ncstData = {}

                for i in responseData:
                    ncstData[i["category"]] = i["obsrValue"] 
            
                return ncstData
            else: raise Exception(f'getNowcast() 비정상 응답 코드 : {response["response"]["header"]["resultCode"]}') # API 응답코드가 비정상일 경우 에러 발생
        except Exception as e: # API 데이터 처리 실패
            logger = setLogger("api", "getNowcastError")
            logger.error("getNowcast API 처리 오류")
            logger.error(e)
            return "ERROR"

async def getForecast(gridX, gridY):
    """
    기상청 OPEN API를 사용해 초단기예보 데이터를 조회하는 함수
    Args:
        gridX (str) : 기상청 Grid 좌표계 X 좌표
        gridY (str) : 기상청 Grid 좌표계 Y 좌표
    """
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
    params = {
        "serviceKey" : openAPIKey,
        "numOfRows" : "30",
        "pageNo" : "1",
        "dataType" : "JSON",
        "base_date" : getDate("fcst"),
        "base_time" : getTime("fcst"),
        "nx" : gridX,
        "ny" : gridY
        }
    
    try: # API 호출 시도 (GET Request)
        response = requests.get(url, params=params, verify=False).json()
    except Exception as e: # API 호출 실패
        logger = setLogger("api", "getForecastError")
        logger.error("getForecast API 호출 오류")
        logger.error(e)
        return "ERROR"
    else: # API 호출 성공
        try: # API 호출 성공 후 데이터 처리
            if response["response"]["header"]["resultCode"] == "00": # API 응답코드 확인
                responseData = response["response"]["body"]["items"]["item"]

                fcstData = {
                    "fcstTime": [],
                    "LGT" : [],
                    "PTY" : [],
                    "RN1" : [],
                    "SKY" : [],
                    "T1H" : [],
                }

                category_keys = fcstData.keys()

                for i in responseData:
                    category = i["category"]
                    if category in category_keys:
                        fcstData[category].append(i["fcstValue"])
                        if category == "LGT":
                            fcstData["fcstTime"].append(i["fcstTime"])

                return fcstData
            else: raise Exception(f'getForecast() 비정상 응답 코드 : {response["response"]["header"]["resultCode"]}') # API 응답코드가 비정상일 경우 에러 발생
        except Exception as e: # API 데이터 처리 실패
            logger = setLogger("api", "getForecastError")
            logger.error("getForecast API 처리 오류")
            logger.error(e)
            return "ERROR"
    