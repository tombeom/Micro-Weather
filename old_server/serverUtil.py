import time
import re
from collections import defaultdict
from apps.logger import setLogger

blockedIP = [] # 임시 차단 IP 리스트
requestIP = defaultdict(list) # 접속 요청한 IP 딕셔너리 {"requestIP": [time, time ... ]}

def checkTempBlock(clientIP):
    """
    limitTime 내에 maxRequest 이상 접속 요청 시 blockTime 동안 접속을 임시로 차단하는(return False) 함수
    Args:
        clientIP (str) : 접속 요청 IP
    """

    blockTime = 1800 # 임시 차단 시간(초)
    maxRequest = 5 # 최대 요청 가능 횟수
    limitTime = 1 # 제한 시간 (초)

    nowTime = time.time() # 현재 시간 값 생성

    if clientIP in blockedIP: # 접속 요청 IP가 임시 차단 IP 리스트에 있을 경우
        if nowTime - requestIP[clientIP][-1] >= blockTime: # 차단 이후 시간 (현재 시간값 - 마지막 접속 시간값) >= 임시 차단 시간일 경우
            requestIP[clientIP] = [] # 접속 시간값 모두 삭제
            blockedIP.remove(clientIP) # 임시 차단 IP 리스트에서 접속 요청 IP 삭제
            return False # 접속 차단 해제 후 정상 요청으로 처리
        return True # 접속 차단
    
    requestIP[clientIP] = requestIP[clientIP] + [nowTime] # 접속 차단 리스트에 없는 IP라면 접속 시간값 리스트에 현재 시간값 추가

    if len(requestIP[clientIP]) >= maxRequest: # 접속 요청 횟수 (시간값 리스트 갯수) <= 최대 요청 가능 횟수
        if nowTime - requestIP[clientIP][0] <= limitTime: # 최초 요청 이후 시간 (현재 시간값 - 처음 시간값) <= 제한 시간
            blockedIP.append(clientIP) # 접속 요청 IP를 임시 차단 리스트에 추가
            return True # 접속 차단

    if nowTime - requestIP[clientIP][0] >= limitTime: # 최초 요청 이후 시간 (현재 시간값 - 처음 시간값) >= 제한 시간
        requestIP[clientIP] = [] # 접속 시간값 모두 삭제

    return False # 접속 허용

def checkQuery(queryString):
    """
    정규표현식을 사용해서 요청 Query String이 조건에 부합하면 dict로 return 해주는 함수
    Args:
        queryString (str) : 요청 Query String
    """
    match = re.match(r"latitude=([0-9.-]+)&longitude=([0-9.-]+)", queryString)
    if match:
        latitude = match.group(1)
        longitude = match.group(2)
        return {"latitude": latitude, "longitude": longitude}
    else:
        return False

def loadBlacklist():
    """
    IP 블랙리스트 txt 내용을 가져와서 list로 return 해주는 함수
    """
    dir =  "./blacklist.txt"
    blacklist = []

    with open(dir, "r") as file:
        for ip in file:
            ip = ip.strip()
            blacklist.append((ip))
    return blacklist

def checkBlacklist(clientIP, blacklist):
    """
    접속 요청 IP가 블랙리스트에 포함되어 있다면 접속 제한 (return True) 하는 함수
    Args:
        clientIP (str) : 접속 요청 IP
        blacklist (list) : IP 블랙리스트
    """
    if clientIP in blacklist:
        return True


def checkRequest(environ, blacklist):
    """
    사용자의 요청이 API 요구 조건에 부합하는지 확인하는 함수
    Args:
        environ (dict) : HTTP 요청에 대한 정보를 담고 있는 환경 변수
        blacklist (list) : IP 블랙리스트
    """
    clientIP = environ.get("REMOTE_ADDR") # 접속 요청 IP
    requestMethod = environ.get("REQUEST_METHOD") # 접속 요청 METHOD
    requestPath = environ.get("PATH_INFO") # 접속 요청 경로
    userAgent = environ.get("HTTP_USER_AGENT") # 접속 요청 USER AGENT
    queryString = environ.get("QUERY_STRING") # 접속 요청 Query String

    logger = setLogger("server", "serverMSG")

    if checkBlacklist(clientIP, blacklist) == True: # 블랙리스트 체크
        logger.warning(f'Banned Client Access {clientIP}')
        return "BANNED"
    if checkTempBlock(clientIP) == True: # 임시 차단 체크
        logger.warning(f'Blocked Client Access {clientIP}')
        return "BLOCKED"
    
    if not requestMethod == "GET": # 요청 METHOD가 GET 여부 체크
        logger.warning(f'WRONG METHOD {requestMethod} {clientIP}')
        return "WRONG METHOD"

    location = checkQuery(queryString) # 요청 Query String을 정규 표현식으로 확인

    if location == False: # 요청 Query String이 정규 표현식 검사를 통과하지 못했을 경우
        if (requestPath) == "/favicon.ico": # favicon 요청했을 경우 (정상적으로 사용 시 favicon 요청 없음. 웹브라우저로 직접 GET 요청 시에 favicon 요청)
            logger.info(f'Favicon Request {clientIP}')
            return "FAVICON"
        else: # 조건에 맞지 않는 쿼리문
            logger.warning(f'WRONG QUERY STRING {clientIP} {queryString}')
            return "WRONG QUERY STRING"
    else: # 모든 조건이 정상일 경우, dict로 위경도 데이터 return
        logger.info(f'{clientIP} - {requestMethod} - {queryString}\n{userAgent}')
        return location