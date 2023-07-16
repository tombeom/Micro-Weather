# Micro-Weather

Micro-Weather는 크롬 확장 프로그램으로 브라우저에서 팝업 형식으로 손쉽게 날씨, 미세먼지 정보 등을 확인할 수 있습니다.

## 기능 및 안내사항

### 기능

- 기상청 초단기실황 관측 값과 초단기예보 데이터로 비교적 정확한 날씨 정보를 제공합니다.
- 팝업 창의 색상은 사용자 위치의 일출 및 일몰 시간에 따라 변화합니다.
- 현재 위치를 기반으로 가장 가까운 대기 측정소의 미세먼지 데이터를 확인할 수 있습니다.

### 안내사항
- 사용을 위해 위치 권한 설정이 필요합니다.

- 한국어 및 대한민국(한반도) 내 위치만 지원합니다.
(Only the Korean language and locations within the Republic of Korea are supported.)

- 사용된 리소스는 Microsoft Fluent UI Emoji를 사용했습니다. (https://github.com/microsoft/fluentui-emoji)

## 사용 기술 및 배포 URL

### 사용 기술

<div>
  <img src="https://img.shields.io/badge/python-3670A0?style=flat-square&logo=python&logoColor=ffdd54"/>
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white"/>
  <img src="https://img.shields.io/badge/Tailwind CSS-06B6D4?style=flat-square&logo=Tailwind CSS&logoColor=white"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black"/>
<div>

### 배포 URL

- [chrome 웹 스토어](https://chrome.google.com/webstore/detail/micro-weather/mkkjhfmhfoniidbdfdndgpegdglfpkbh?hl=ko&authuser=0)

## 기타

### 작동 사진
<div>
  <img src="https://lh3.googleusercontent.com/1cRghi0kji-8IS4UatKM_56hPYdjut8UcwLDUDCurnuDpdtztj5oU_bv3HC4xL0EWAhd7vLgvtOGWd0QDjHKxXXxV7I"/>
  <img src="https://lh3.googleusercontent.com/IWepTl9O8oKw36G3gpTtrcxzrbzYnI4IHYMCeNrbiUo10BQmWzaT4DCx8FI4NrS8obETGa_Od6RiHOavH0H1KPDC"/>
  <img src="https://lh3.googleusercontent.com/GKrJOSxTnwkPjRwMk8fQ4rJn39oC8RsF4K96CRuIkVRI16Dno5RyjYa58vKZ7MAN3t2jRURJlcepOYdrbARwJ3kDhLE"/>
<div>

### 개발과정과 시행착오
- 서버 구축 과정
```
처음 만들었던 Micro-Weather-Standalone (https://github.com/tombeom/Micro-Weather-Standalone) 은
별도의 서버 없이 JavaScript만을 이용해서 직접 API 호출을 하는 방식으로 제작되었다.
하지만 크롬 확장 프로그램에서는 API 키를 숨길 수 있는 방법이 없었고
API 키가 그대로 노출되기 때문에 만약 누군가 마음만 먹으면 내 API 키를 사용할 수 있었다.
개인적으로 사용하는 것은 문제가 없지만 이대로 배포할 수는 없었다.

기상청 API 호출 시 Document에 안내된 부분과 다른 부분도 있었고 서버 지연 등의 문제로 가끔 데이터가 누락되거나 늦게 생성되는 경우도 있었다.
이 경우 사용자에게 불편을 줄 수 있고 여러 개의 API가 비동기식으로 호출되다 보니 속도가 달라 화면을 불러오는데 일관성이 떨어지기도 했다.

결국 클라이언트에서 요청이 있을 때 서버 측에서 여러 API를 호출하고 내가 필요한 데이터들을 JSON 형태로 return 해준다면
속도는 조금 오래 걸릴 수 있지만 데이터 처리나 일관성 측면에서는 더 좋을 것이라고 판단해서 서버를 구축하게 되었다.

서버는 Python으로 작성되었고
웹 프레임워크를 사용하려고 했는데 Django는 너무 무거울 것 같았고
Flask나 FastAPI도 내가 필요한 기능에 비해 굳이 필요 없을 것 같다는 생각이 들어
HTTP 요청 처리에 대한 공부 겸 Python에 내장된 wsgiref 라이브러리를 사용해
직접 Request(Get)를 처리해 보기로 했다.
```

- 서버 어뷰징
```
서버를 열어놓게 되면 어드민 페이지에 접속을 시도한다거나
흔히 알려진 취약점 공격을 위한 요청 등 각종 어뷰징이 발생하게 된다.

일단 소프트웨어적인 처리로 내가 원하는 방식의 쿼리 값이 아닌 경우라면 요청을 받아주지 않고
짧은 시간 내 많은 요청이 올 경우 429 Too Many Requests를 return
악성 이용자의 경우 블랙리스트를 통한 403 Forbidden을 return 해주고 있는데

이런 방식의 소프트웨어적인 처리로는 서버의 한계를 넘는 DDOS 공격이 있을 때 버티기는 힘들 것 같다는 생각을 한다.
물리적인 방화벽 등을 사용하면 좋겠지만 소규모 API 서버에서는 비용 문제로 적용이 쉽지 않다.
```

- 추가된 기능
```
기존 클라이언트에서 API를 호출하는 방식보다 응답 시간이 길어졌기 때문에
로딩 화면을 추가로 만들었고 요청에 실패했을 때나 위치 권한을 받지 못했을 때 띄울 화면도 추가했다.

또 기존에는 가장 가까운 대기 측정소 한곳만 호출하여 측정소 고장이나 통신 오류 시 미세먼지 데이터 값을 보여줄 수 없었지만
지금은 서버 측에서 위와 같은 상황이 발생하면 두 번째로 가까운 대기 측정소의 데이터를 가져오도록 만들었다.
(응답 시간은 더 길어지지만 좀 더 안정적으로 데이터를 보여줄 수 있다.)
(설마설마했지만 악천후 시에는 두 곳 모두 데이터를 가져오지 못하는 경우도 있었다......)
```

- 시행착오와 공부해 볼 것
```
1. 처음 서버를 만들고 요청을 보내보았을 때 CORS 에러가 발생하여 응답 헤더에 CORS를 추가해주었다.
하지만 이후 도메인을 구입하고 도메인을 단순하게 리다이렉트 방식으로 설정하니 다시 CORS 에러가 발생하였다.
요청되는 URL이 중간에 바뀌기 때문인 것 같아 위 방식 대신 사용 중인 클라우드 서버의 DNS로 연결해 (정석 방법) 문제를 해결했지만
이런 경우 Cloudflare를 사용할 수 있을까? 

2. 서버에 많은 요청이 들어올 경우 로그를 터미널에 print 한다면 부하도 늘어나게 되고 읽기도 힘들어진다.
Python의 logger를 이용해 서버의 히스토리(접속 요청이나 에러)를 기록했다.
사용이 미숙해 log가 두 번씩 생기기도 했지만 현재는 수정한 상태이다.

3. 처음에는 서버 내 API 요청 코드를 동기식으로 작성했는데
응답 시간이 너어어어무 길어져 asyncio를 이용해 비동기식으로 바꾸어주었다.
실행 속도가 유의미하게 개선되었지만 만족스러운 속도는 아니었다.
찾아보니 Python requests 모듈 자체가 동기 방식이기 때문에 속도 개선에 한계가 있는 것 같았다.
aiohttp 모듈을 사용하는 방식으로 속도 개선의 여지를 남겨두었다. (예정)
```
