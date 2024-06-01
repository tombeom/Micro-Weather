// index.html 로드 시 사용자의 위치 정보를 받아오고 API를 통해 데이터를 받아오는 javascript

/**
 * 사용자의 위치 정보를 가지고 API 호출하는 함수. 호출 성공 이후 drawPopup() 실행
 * @param {Object} position 
 */
async function getData(position) {
  const url = "http://tombeom.com/";
  const params = {
    latitude: position.coords.latitude,
    longitude: position.coords.longitude,
  };
  const requestUrl = `${url}?${new URLSearchParams(params).toString()}`;
  const c = await fetch(requestUrl)
    .then((res) => res.json())
    .then((res) => {
      drawPopup(res);
    })
    .catch((e) => {
      showFailure(
        "서버와 통신에 문제가 있어요...", 
        "팝업을 다시 열어 시도해 보세요.",
      );
    });
}

/**
 * 사용자의 위치(위경도 데이터)를 불러오면서 에러가 발생했을 때 실행되는 함수
 * @param {Object} e
 */
function getPositionError(e) {
  switch (e.code) {
    case 1:
      showFailure(
        "확장 프로그램의 위치 권한을 허용하고 다시 팝업을 열어주세요!", 
        "현재 위치 권한이 거부되어 있어요. 날씨를 불러오기 위해서는 사용자의 위치 권한이 필요해요."
      ); // PERMISSION_DENIED
      break;
    case 2:
      showFailure(
        "현재 위치 정보를 사용할 수 없어요...",
        "실행 환경을 확인하고 다시 팝업을 열어 시도해 보세요."
      ); // POSITION_UNAVAILABLE
      break;
    case 3:
      showFailure(
        "위치 정보를 가져오는데 너무 오래 걸려요...", 
        "다시 팝업을 열어 시도해 보세요.",
      ); // TIMEOUT
      break;
  }
}

/**
 * API 호출 성공 후 화면을 그려주는 함수
 * @param {Object} pmGradeData 
 */
function drawPopup(data) {
  hideLoading();
  showPMDataSrcInfo();
  setBG(data);
  drawPosition(data);
  drawNcst(data);
  drawFcst(data);
  drawPM(data);
}

// 현재 위경도 좌표를 받아오고 API 호출
navigator.geolocation.getCurrentPosition(
  getData,
  getPositionError,
  (options = {
    enableHighAccuracy: true,
    timeout: 5000,
    maximumAge: 0,
  })
);