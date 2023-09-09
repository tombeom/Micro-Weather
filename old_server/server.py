import asyncio
from wsgiref.simple_server import make_server
from serverResponse import getResponseData
from serverUtil import *

IP = "0.0.0.0" # 서버 IP 설정
PORT = 80 # 서버 PORT 설정

def application(environ, startResponse): # 요청이 들어왔을 때 실행되는 함수

    checkedValue = checkRequest(environ, blacklist)

    if checkedValue == "BANNED":
        startResponse("403 Forbidden", [("Content-type", "text/plain; charset=utf-8")])
        return [b"403 Forbidden"]
    elif checkedValue == "BLOCKED":
        startResponse("429 Too Many Requests", [("Content-type", "text/plain; charset=utf-8")])
        return [b"429 Too Many Requests"]
    elif checkedValue == "FAVICON":
        startResponse("200 OK", [("Content-type", "text/plain; charset=utf-8")])
        return [b"No Favicon"]
    elif checkedValue == "WRONG METHOD":
        startResponse("405 Method Not Allowed", [("Content-type", "text/plain; charset=utf-8")])
        return [b"405 Method Not Allowed"]
    elif checkedValue == "WRONG QUERY STRING":
        startResponse("400 Bad Request", [("Content-type", "text/plain; charset=utf-8")])
        return [b"400 Bad Request"]
    else:
        location = checkedValue
        latitude = float(location["latitude"])
        longitude = float(location["longitude"])
        data = asyncio.run(getResponseData(latitude, longitude))
        if data == False:
            headers = [("Content-type", "text/plain; charset=utf-8")]
            headers.append(('Access-Control-Allow-Origin', '*'))
            startResponse("200 OK", headers)
            responseBody = "API 요청 위치가 대한민국인지 확인해 주세요"
            return [responseBody.encode("utf-8")]
        else:
            headers = [("Content-type", "application/json; charset=utf-8")]
            headers.append(('Access-Control-Allow-Origin', '*'))
            startResponse("200 OK", headers)
            return [data.encode("utf-8")]

blacklist = loadBlacklist() # 블랙리스트 불러오기
httpd = make_server(IP, PORT, application) # 서버 시작
print(f'* Server Running On http://{IP}:{PORT}') # 서버 시작 메시지 콘솔 출력

try:
    httpd.serve_forever() # 서버 계속 실행
except KeyboardInterrupt: # Ctrl + C 입력 시 서버 종료
    print("Server Shutting Down...") # 서버 종료 메시지 콘솔 출력
    httpd.shutdown() # 서버 종료
    print("Server Closed") # 서버 종료 후 메시지 콘솔 출력