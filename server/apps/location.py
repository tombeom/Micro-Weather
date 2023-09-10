import math
import requests
import os
from apps.utils import fetch

def checkCoord(latitude, longitude):
    """
    사용자의 위경도가 한반도(남한) 내에 위치해있는지 확인하는 함수
    Args:
        latitude (str) : 위도
        longitude (str) : 경도
    """
    FAREAST = 131.87222222
    FARWEST = 125.06666667
    FARNORTH = 38.45000000
    FARSOUTH = 33.10000000

    if (float(latitude) < FARSOUTH or float(latitude) > FARNORTH) or (float(longitude) < FARWEST and float(longitude) > FAREAST):
        return False
    else: return True

async def convertCoordToAddress(latitude, longitude):
    """
    Nominatim API를 사용해 위경도 데이터를 역지오코딩 하여 OpenStreetMap의 주소로 변환하는 함수
    Args:
        latitude (str) : 위도
        longitude (str) : 경도
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format" : "json",
        "lat" : latitude,
        "lon" : longitude,
        "zoom": "18"
    }
    response = await fetch(url, params = params)

    return response["address"]

def convertCoordToTM(latitude, longitude):
    """
    kakao REST API를 사용해 위경도 데이터를 TM 중부원점 좌표계 데이터로 변환하는 함수
    Args:
        latitude (str) : 위도
        longitude (str) : 경도
    """
    url = "https://dapi.kakao.com/v2/local/geo/transcoord"
    params = {
    "x": longitude,
    "y": latitude,
    "output_coord": "TM",
    }
    headers = {
        "Authorization": "KakaoAK " + os.getenv("kakaoAPIKey")
    }

    response = requests.get(url, params = params, headers = headers).json()

    return response["documents"][0]

def convertCoordToGrid(latitude, longitude):
    """
    위경도 데이터를 단기예보 API에서 사용하는 기상청 좌표계 데이터로 변환하는 함수
    Args:
        latitude (str) : 위도
        longitude (str) : 경도
    """
    EARTHRADIUS = 6371.00877
    GRIDSCALE = 5.0
    STANDARDPARALLELLATITUDE1 = 30.0
    STANDARDPARALLELLATITUDE2 = 60.0
    ORIGINLATITUDE = 38.0
    ORIGINLONGITUDE = 126.0
    ORIGINLATITUDETOGRID = 43
    ORIGINLONGITUDETOGRID = 136

    oneDegree = math.pi / 180.0

    re = EARTHRADIUS / GRIDSCALE
    slat1 = STANDARDPARALLELLATITUDE1 * oneDegree
    slat2 = STANDARDPARALLELLATITUDE2 * oneDegree
    olon = ORIGINLONGITUDE * oneDegree
    olat = ORIGINLATITUDE * oneDegree

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = (math.pow(sf, sn) * math.cos(slat1)) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = (re * sf) / math.pow(ro, sn)

    ra = math.tan(math.pi * 0.25 + float(latitude) * oneDegree * 0.5)
    ra = (re * sf) / math.pow(ra, sn)
    theta = float(longitude) * oneDegree - olon
    if (theta > math.pi): theta -= 2.0 * math.pi
    if (theta < -math.pi): theta += 2.0 * math.pi
    theta *= sn

    gridX = math.floor(ra * math.sin(theta) + ORIGINLATITUDETOGRID + 0.5)
    gridY = math.floor(ro - ra * math.cos(theta) + ORIGINLONGITUDETOGRID + 0.5)

    gridCoord = {"gridX" : gridX, "gridY" : gridY}

    return gridCoord