import os
from apps.utils import fetch

async def getStationInfo(tmX, tmY):
    """
    한국환경공단 OPEN API를 사용해 TM 좌표 기반 근접 측정소 목록을 불러오는 함수
    Args:
        tmX (str) : TM 중부원점 좌표계 X 좌표
        tmY (str) : TM 중부원점 좌표계 Y 좌표
    """
    url = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList"
    params = {
        "serviceKey" : os.getenv("openAPIKey"),
        "returnType" : "json",
        "tmX" : tmX,
        "tmY" : tmY,
        "ver" : "1.1"
    }
    
    try: # API 호출 시도 (GET Request)
        response = await fetch(url, params=params)
    except Exception as e: # API 호출 실패
        return "ERROR"
    else: # API 호출 성공
        try: # API 호출 성공 후 데이터 처리
            if response["response"]["header"]["resultCode"] == "00": # API 응답코드 확인
                # 응답코드가 정상 값이면 데이터 return
                stationList = []

                for i in response["response"]["body"]["items"]:
                    stationList.append(i["stationName"])

                return stationList
            else: raise Exception(f'getStationInfo() 비정상 응답 코드 : {response["response"]["header"]["resultCode"]}') # API 응답코드가 비정상일 경우 에러 발생
        except Exception as e: # API 데이터 처리 실패
            return "ERROR"

async def getPMData(stationList):
    """
    한국환경공단 OPEN API를 사용해 측정소명으로 실시간 대기 측정 정보를 조회하는 함수
    Args:
        stationList (list) : 좌표 근접측정소 리스트
    """
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
    params = {
        "serviceKey": os.getenv("openAPIKey"),
        "returnType": "json",
        "stationName": stationList[0],
        "dataTerm": "DAILY",
        "ver": "1.4",
        }
    
    try: # API 호출 시도 (GET Request)
        response = await fetch(url, params=params)
    except Exception as e: # API 호출 실패
        return "ERROR"
    else: # API 호출 성공
        try: # API 호출 성공 후 데이터 처리
            if response["response"]["header"]["resultCode"] == "00": # API 응답코드 확인
                # 응답코드가 정상 값이면 데이터 return
                particulateMatterData = {}
                particulateMatterData["stationName"] = response["response"]["body"]["items"][0]["stationName"]
                particulateMatterData["pm10Value"] = response["response"]["body"]["items"][0]["pm10Value"]
                particulateMatterData["pm25Value"] = response["response"]["body"]["items"][0]["pm25Value"]

                return particulateMatterData
            else: raise Exception(f'getPMData() 비정상 응답 코드 : {response["response"]["header"]["resultCode"]}')  # API 응답코드가 비정상일 경우 에러 발생
        except Exception as e:  # API 데이터 처리 실패 시 다음 측정소로 API 재호출 시도
            params["stationName"] = stationList[1]
            try: # 다음 측정소로 API 재호출 시도 (GET Request)
                response = await fetch(url, params=params)
            except Exception as e: # API 재호출 실패
                return "ERROR"
            else: # API 재호출 성공
                try: # API 재호출 성공 후 데이터 처리
                    if response["response"]["header"]["resultCode"] == "00": # API 응답코드 확인
                        # 응답코드가 정상 값이면 데이터 return
                        particulateMatterData = {}
                        particulateMatterData["stationName"] = response["response"]["body"]["items"][0]["stationName"]
                        particulateMatterData["pm10Value"] = response["response"]["body"]["items"][0]["pm10Value"]
                        particulateMatterData["pm25Value"] = response["response"]["body"]["items"][0]["pm25Value"]

                        return particulateMatterData
                    else: raise Exception(f'getPMData() 비정상 응답 코드 : {response["response"]["header"]["resultCode"]}')  # API 응답코드가 비정상일 경우 에러 발생
                except Exception as e: # API 데이터 처리 실패
                    return "ERROR"