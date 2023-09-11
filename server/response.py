from apps.location import *
from apps.particulateMatter import *
from apps.sunRiseSet import *
from apps.weather import *

async def getResponseData(latitude, longitude):
    """
    입력받은 사용자의 위경도 데이터로 API를 호출하고 결과값을 JSON으로 return 해주는 함수
    Args:
        latitude (str) : 위도
        longitude (str) : 경도
    """
    # 사용자의 위도, 경도가 대한민국(한반도) 내에 위치할 경우에만 return JSON else return False
    if(checkCoord(latitude, longitude)):
        gridCoord = convertCoordToGrid(latitude, longitude)
        tmCoord = convertCoordToTM(latitude, longitude)
        
        responseData = {}
        responseData["address"] = await convertCoordToAddress(latitude, longitude)
        responseData["sunRiseSetData"] = await getSunRiseSet(latitude, longitude)
        responseData["nowcast"] = await getNowcast(gridCoord["gridX"], gridCoord["gridY"])
        responseData["forecast"] = await getForecast(gridCoord["gridX"], gridCoord["gridY"])
        responseData["pmData"] = await getPMData(await getStationInfo(tmCoord["x"], tmCoord["y"]))
        
        return responseData
    else:
        return False