import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setLogger (type, logName):
    """
    로그 메시지를 작성해주는 함수
    Args:
        type (str) : API와 서버 로그 저장 위치 구분
        logName (str) : 로그 파일이 작성될 파일명
        level (int) : 10: DEBUG, 20: INFO, 30: WARNING, 40: ERROR, 50: CRITICAL
        msg (str) : 로그에 작성할 메시지
    """

    if (type == "server"):
        logDir = "log/server/"
        logFileName = "server.log"
    elif (type == "api"):
        logDir = "log/api/"
        logFileName = logName + ".log"
    else:
        logDir = "log/"
        logFileName = logName + ".log"

    if not os.path.exists(logDir):
        os.makedirs(logDir)

    logger = logging.getLogger(logName)

    if len(logger.handlers) > 0:
        return logger
        
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(datefmt="%Y/%m/%d %H:%M:%S", fmt='%(asctime)s - [%(levelname)s | %(name)s | %(filename)s:%(lineno)s] > %(message)s')

    handler = TimedRotatingFileHandler(filename=logDir + logFileName, when='midnight', interval=1, encoding="utf-8")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
