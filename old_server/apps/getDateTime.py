from datetime import datetime, timedelta

def getDate(type=False):
    """
    현재 날짜를 API 호출 시 사용되는 포맷에 맞게 return 해주는 함수
    Args:
        type (str) : ncst, fcst
    """
    todayDate = datetime.today()
    if (type == "ncst"):
        if (datetime.now().hour == 0):
            if (datetime.now().minute < 30):
                return (todayDate - timedelta(days=1)).strftime("%Y%m%d")
        else:
            return todayDate.strftime("%Y%m%d")
    elif (type == "fcst"):
        if (datetime.now().hour == 0):
            if (datetime.now().minute < 45):
                return (todayDate - timedelta(days=1)).strftime("%Y%m%d")
        else:
            return todayDate.strftime("%Y%m%d")
    else:
        return todayDate.strftime("%Y%m%d")

def getTime(type=False):
    """
    현재 시각을 API 호출 시 사용되는 포맷에 맞게 return 해주는 함수
    Args:
        type (str) : ncst, fcst
    """
    nowTime = datetime.now()
    if (type == "ncst"):
        # ncst 요청 시 API 제공 시간 30분 이후
        ncstServeMinute = 30
        if (nowTime.minute < ncstServeMinute):
            return (nowTime - timedelta(hours=1)).strftime("%H") + "00"
        else:
            return datetime.now().strftime("%H") + "00"
    elif (type == "fcst"):
        fcstServeMinute = 45
        if (nowTime.minute < fcstServeMinute):
            return (nowTime - timedelta(hours=1)).strftime("%H") + "00"
        else: 
            return datetime.now().strftime("%H") + "00"
    else:
        return datetime.now().strftime("%H%M")
    