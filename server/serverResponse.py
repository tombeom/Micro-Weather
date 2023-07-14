import json
import time
from apps.logger import setLogger
from apps.weather import *
from apps.sunRiseSet import *
from apps.location import *
from apps.getDateTime import *
from apps.particulateMatter import *

async def getResponseData(latitude, longitude):
    """
    입력받은 사용자의 위경도 데이터로 API를 호출하고 결과값을 JSON으로 return 해주는 함수
    Args:
        latitude (str) : 위도
        longitude (str) : 경도
    """
    logger = setLogger("server", "serverMSG")
    if(checkCoord(latitude, longitude)):
        startTime = time.perf_counter()
        logger.info(f'Processing - latitude: {latitude}, longitude: {longitude}')
        gridCoord = convertCoordToGrid(latitude, longitude)
        tmCoord = convertCoordToTM(latitude, longitude)

        responseData = {}
        responseData["address"] = await convertCoordToAddress(latitude, longitude)
        responseData["sunRiseSetData"] = await getSunRiseSet(latitude, longitude)
        responseData["nowcast"] = await getNowcast(gridCoord["gridX"], gridCoord["gridY"])
        responseData["forecast"] = await getForecast(gridCoord["gridX"], gridCoord["gridY"])
        responseData["pmData"] = await getPMData(await getStationInfo(tmCoord["x"], tmCoord["y"]))

        responseJson = json.dumps(responseData, indent=4, ensure_ascii=False)
        endTime = time.perf_counter()
        processingTime = endTime - startTime
        logger.info(f'Success - Processing Time : {processingTime}')
        return(responseJson)

    else:
        logger.info(f'The Coordinates are outside South Korea - latitude: {latitude}, longitude: {longitude}')
        return False