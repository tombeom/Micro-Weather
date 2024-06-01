// API 데이터를 받아온 후 데이터를 HTML로 출력하는 javascript

// 데이터 출력 위치를 지정하기 위한 QuerySelector
// 기타
const $popup = document.querySelector("#popup");
const $loadingScreen = document.querySelector("#loadingScreen");
const $failureScreen = document.querySelector("#failureScreen");
// 초단기실황
const $ncstImg = document.querySelector("#ncstImg");
const $ncstPrecipitationImg = document.querySelector("#ncstPrecipitationImg")
const $ncstTemp = document.querySelector("#ncstTemp");
const $location = document.querySelector("#location");
const $ncstPrecipitation = document.querySelector("#ncstPrecipitation");
const $ncstHumidity = document.querySelector("#ncstHumidity");
// 미세먼지
const $pmDataSrcInfoIcon = document.querySelector("#pmDataSrcInfoIcon");
const $pmDataSrcInfo = document.querySelector("#pmDataSrcInfo");
const $pmDataSrcInfoMsg = document.querySelector("#pmDataSrcInfoMsg");
const $station = document.querySelector("#station");
const $pm25 = document.querySelector("#pm25");
const $pm25Grade = document.querySelector("#pm25Grade");
const $pm10 = document.querySelector("#pm10");
const $pm10Grade = document.querySelector("#pm10Grade");
// 초단기예보
const $fcstData = document.querySelector("#fcstData");

// 기상 상태 이미지
const imgData = [
  {
    idx: "0",
    src: "images/clear.png",
    alt: "맑음",
    id: "clear",
  },
  {
    idx: "1",
    src: "images/mostlyCloudy.png",
    alt: "구름많음",
    id: "mostlyCloudy",
  },
  {
    idx: "2",
    src: "images/cloudy.png",
    alt: "흐림",
    id: "cloudy",
  },
  {
    idx: "3",
    src: "images/rain.png",
    alt: "비 혹은 비/눈",
    id: "rain",
  },
  {
    idx: "4",
    src: "images/snow.png",
    alt: "눈",
    id: "snow",
  },
  {
    idx: "5",
    src: "images/shower.png",
    alt: "빗방울 혹은 빗방울눈날림 (강수량 0.1mm 미만)",
    id: "shower",
  },
  {
    idx: "6",
    src: "images/snowDrifting.png",
    alt: "눈날림 (적설량 0.1cm 미만)",
    id: "snowDrifting",
  },
  {
    idx: "7",
    src: "images/lightning.png",
    alt: "낙뢰",
    id: "lightning",
  },
  {
    idx: "8",
    src: "images/thunderStorm.png",
    alt: "뇌우",
    id: "thunderStorm",
  },
  {
    idx: "9",
    src: "images/rainUmbrella.png",
    alt: "비 오는 우산",
    id: "rainUmbrella",
  },
  {
    idx: "10",
    src: "images/foldedUmbrella.png",
    alt: "접힌 우산",
    id: "foldedUmbrella",
  },
];

/**
 * 일출, 일몰 데이터를 바탕으로 body Backgroud Color를 설정하는 함수
 * @param {Object} data 
 */
function setBG(data) {
  if (data.sunRiseSetData.sunRiseSetData === "sunrise") {
    // 이외에는 밝은 배경색 설정 (일출 시간 이후, 일몰 시간 전)
    $popup.style.backgroundColor = "#5490e5";
  } else if (data.sunRiseSetData.sunRiseSetData === "sunset") {
    // 일몰 시간 이후, 일출 시간 전에는 어두운 배경색 설정
    $popup.style.backgroundColor = "#1f242e";
  }
}

/**
 * 사용자의 위치(시군구, 읍면동)를 출력하는 함수
 * @param {Object} data 
 */
function drawPosition(data) {
  $location.innerText = `${data.address.city} ${data.address.quarter}`;
}

/**
 * API 호출이 성공했을 때 로딩 화면을 숨기는 함수
 */
function hideLoading() {
  $loadingScreen.style.display = "none";
}

/**
 * API 호출이 실패했을 때 실패 화면을 띄우는 함수
 */
function showFailure(msg1, msg2) {
  $failureScreen.style.display = "block";
  document.querySelector("#failureMsg1").innerText = msg1
  document.querySelector("#failureMsg2").innerText = msg2
}

/**
 * 미세먼지 데이터 출처 및 오류 가능성 메시지 출력 함수
 */
function showPMDataSrcInfo() {
  $pmDataSrcInfoIcon.addEventListener("click", function() {
    $pmDataSrcInfo.style.display = "block";
    setTimeout(function () {
      $pmDataSrcInfoMsg.style.opacity = 0;
      $pmDataSrcInfoMsg.style.transition = "opacity 1s ease"
    }, 2000);
    setTimeout(function () {
      $pmDataSrcInfo.style.display = "none";
      $pmDataSrcInfoMsg.style.opacity = 0.9;
    }, 2600);
  });
}

/**
 * 초단기실황 데이터를 출력하는 함수
 * @param {Object} data
 */
function drawNcst(data) {
  // 날씨에 맞는 이미지를 불러와서 적용
  const weatherImg = getWeatherImage(data.forecast.LGT[0], data.nowcast.PTY, data.forecast.SKY[0], data.nowcast.RN1);
  $ncstImg.src = weatherImg.src;
  $ncstImg.alt = weatherImg.alt;

  // 강우 여부에 따라 강수량 우산 이미지 설정
  const umbrellaImg = getUmbrellaImg(data.nowcast.RN1);
  $ncstPrecipitationImg.src = umbrellaImg.src;
  $ncstPrecipitationImg.alt = umbrellaImg.alt;

  // 초단기 실황 데이터 값 출력
  $ncstTemp.innerText = `${data.nowcast.T1H}°`;
  $ncstPrecipitation.innerText = `강수량 ${data.nowcast.RN1} mm`;
  $ncstHumidity.innerText = `습도 ${data.nowcast.REH} %`;
}

/**
 * 초단기예보 데이터를 출력하는 함수
 * @param {Object} data
 */
function drawFcst(data) {

  // 총 6개의 초단기예보 데이터를 출력
  for (let i = 0; i < data.forecast.fcstTime.length; i++) {
    const weatherImg = getWeatherImage(data.forecast.LGT[i], data.forecast.PTY[i], data.forecast.SKY[i], data.forecast.RN1[i]);
    const umbrellaImg = getUmbrellaImg(data.forecast.RN1[i]);
    let rn1Str = "";
    const rn1 = data.forecast.RN1[i];

    //초단기예보과 초단기실황의 강수 값이 달라 수정
    if (rn1 === "0") {
      rn1Str = `강수 없음`;
    } else {
      rn1Str = `${rn1}`;
    }
    
    // 초단기예보 출력을 위한 HTML
    const fcstDataForm = `
        <li>
          <div class="pl-5">
            <div class="flex mb-2">
              <img class="w-6 mr-2" src="${weatherImg.src}" alt="${weatherImg.alt}" />
              <p>${data.forecast.T1H[i]}°</p>
            </div>
            <div class="flex mb-2 font-pretendard">
              <img class="w-6 mr-2" src="${umbrellaImg.src}" alt="${umbrellaImg.alt}" />
              <p>${rn1Str}</p>
            </div>
            <h3 class="font-bold text-center">${data.forecast.fcstTime[i].slice(0, 2)}:00</h3>
          </div>
        </li>
      `;

    // 초기단기예보 데이터 출력
    $fcstData.insertAdjacentHTML("beforeend", fcstDataForm);
  }
}

/**
 * 미세먼지 데이터를 출력하는 함수
* @param {Object} data 
 */
function drawPM(data) {
  const pm = checkPM(data);

  $station.innerText = `${data.pmData.stationName} 측정소`;
  $pm25.innerText = `${pm.pm25Value}`;
  $pm25.style.backgroundColor = setPMBackgroundColor(pm.pm25Grade);
  $pm25Grade.innerText = `${pm.pm25Grade}`;
  $pm10.innerText = `${pm.pm10Value}`;
  $pm10.style.backgroundColor = setPMBackgroundColor(pm.pm10Grade);
  $pm10Grade.innerText = `${pm.pm10Grade}`;
}

/**
 * API로부터 받아온 미세먼지 데이터를 가져와서 값을 확인 및 수정하고 return 해주는 함수
 * @param {Object} data 
 */
function checkPM(data) {
  // return 할 미세먼지 데이터
  let returnData = {
    pm10Value: "",
    pm25Value: "",
    pm10Grade: "",
    pm25Grade: "",
  };

  // 미세먼지 값이 있다면 checkPMGrade() 실행해서 미세먼지 등급 저장. 그렇지 않다면 "데이터 없음"을 return
  if (data.pmData.pm10Value != "-") {
    returnData.pm10Value = data.pmData.pm10Value;
    returnData.pm10Grade = checkPMGrade("pm10", data.pmData.pm10Value);
  } else {
    returnData.pm10Value = "-";
    returnData.pm10Grade = "데이터 없음";
  }

  if (data.pmData.pm25Value != "-") {
    returnData.pm25Value = data.pmData.pm25Value;
    returnData.pm25Grade = checkPMGrade("pm25", data.pmData.pm25Value);
  } else {
    returnData.pm25Value = "-";
    returnData.pm25Grade = "데이터 없음";
  }
  return returnData
}

/**
 * 미세먼지 값을 받아서 등급 값을 String Type으로 return 해주는 함수
 * @param {String} type
 * @param {String} pmGradeData 
 */
function checkPMGrade(type, pmGradeData) {
  if (type === "pm10") {
    // PM 10 미세먼지 값이 들어왔을 때 기준
    if (pmGradeData > 0 && pmGradeData <= 30) {
      return "좋음";
    } else if (pmGradeData >= 31 && pmGradeData <= 80) {
      return "보통";
    } else if (pmGradeData >= 81 && pmGradeData <= 150) {
      return "나쁨";
    } else if (pmGradeData >= 151) {
      return "매우 나쁨";
    } else {
      return "데이터 없음";
    }
  } else if (type === "pm25") {
    // PM 2.5 미세먼지 값이 들어왔을 때 기준
    if (pmGradeData > 0 && pmGradeData <= 15) {
      return "좋음";
    } else if (pmGradeData >= 16 && pmGradeData <= 35) {
      return "보통";
    } else if (pmGradeData >= 36 && pmGradeData <= 75) {
      return "나쁨";
    } else if (pmGradeData >= 76) {
      return "매우 나쁨";
    } else {
      return "데이터 없음";
    }
  }
}

/**
 * 미세먼지 등급 값을 받아서 등급에 맞는 Background Color를 String Type으로 return 해주는 함수
 * @param {String} pmGradeData 
 */
function setPMBackgroundColor (pmGradeData) {
  if (pmGradeData === "좋음") {
    return "#5ca0ff";
  } else if (pmGradeData === "보통") {
    return "#5cc339";
  } else if (pmGradeData === "나쁨") {
    return "#eda05c";
  } else if (pmGradeData === "매우 나쁨") {
    return "#ea665c";
  } else {
    return "";
  }
}

/**
 * 각 예보 별 값을 받아서 상황에 맞는 날씨 별 이미지를 return 해주는 함수
 * @param {String} lightning
 * @param {String} precipitationType
 * @param {String} sky
 * @param {String} rn1
 */
function getWeatherImage(lightning, precipitationType, sky, rn1) {
  if (lightning === "0") {
    // 번개 칠 때
    if (precipitationType === "0") {
      // 비가 안올 때
      if (rn1 != "강수없음" && rn1 > 0) {
        // 강수형태 값이 0이지만 강수량이 있을 때 - shower.png
        return imgData[5];
      } else {
        if (sky === "1") {
          // 맑음 (구름이 0~5할의 상태) - clear.png
          return imgData[0];
        } else if (sky === "3") {
          // 구름많음 (구름이 6~8할의 상태) - mostlyCloudy.png
          return imgData[1];
        } else if (sky === "4") {
          // 흐림 (구름이 9~10할의 상태) - cloudy.png
          return imgData[2];
        }
      }
    } else if (precipitationType === "1" || precipitationType === "2") {
      // 비 or 비/눈 - rain.png
      return imgData[3];
    } else if (precipitationType === "3") {
      // 눈 - snow.png
      return imgData[4];
    } else if (precipitationType === "5" || precipitationType === "6") {
      // 빗방울 or 빗방울눈날림 (비 0.1mm 미만) - shower.png
      return imgData[5];
    } else if (precipitationType === "7") {
      // 눈날림 (눈 0.1cm 미만) - snowDrifting.png
      return imgData[6];
    }
  } else if (lightning < 0) {
    // 번개 안칠 때
    if (rn1 != "강수없음" || "0") {
      // 번개 치는데 비가 안올 때 - lightning.png
      return imgData[7];
    } else {
      // 번개 치면서 비도 올 때 - thunderStorm.png
      return imgData[8];
    }
  }
}

/**
 * 1시간 강수량 값을 받아서 상황에 맞는 강수량 이미지를 return 해주는 함수
 * @param {String} rn1 
 */
function getUmbrellaImg(rn1) {
  if (rn1 != "강수없음" && rn1 != "0") {
    return imgData[9]; // 비 오는 우산 - images/rainUmbrella.png
  } else {
    return imgData[10]; // 접힌 우산 - images/foldedUmbrella.png
  }
}

