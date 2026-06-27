const game = {
  attempts: 9, //남은 시도 횟수
  answer: [], //랜덤 숫자 들어갈 곳
  isOver: false, //게임 끝났는지
};

const number1 = document.getElementById("number1");
const number2 = document.getElementById("number2");
const number3 = document.getElementById("number3");
const inputs = [number1, number2, number3];

const attemptsSpan = document.getElementById("attempts");
const resultsDiv = document.getElementById("results");
const resultImg = document.getElementById("game-result-img");
const submitButton = document.querySelector(".submit-button");

//중복되지 않는 3개의 랜덤한 숫자 설정
function random_number() {
  const numbers = [];

  while (numbers.length < 3) {
    const randomNumber = Math.floor(Math.random() * 10);

    if (!numbers.includes(randomNumber)) {
      numbers.push(randomNumber);
    }
  }

  return numbers;
}

//html의 input 내용 비우기
function clear_inputs() {
  inputs.forEach((input) => {
    input.value = "";
  });

  number1.focus();
}

//시도 가능 횟수 설정
function update_attempts() {
  attemptsSpan.textContent = game.attempts;
}

//게임 초기화 설정
function init_game() {
  game.attempts = 9;
  game.answer = random_number();
  game.isOver = false;

  clear_inputs();
  update_attempts();
  resultsDiv.innerHTML = ""; //결과창 삭제
  resultImg.src = ""; //이미지 삭제
  submitButton.disabled = false; //확인하기 버튼
}

//사용자가 입력한 숫자 가져오기
function get_input_numbers() {
  return inputs.map((input) => input.value);
}

function has_empty_input(inputNumbers) {
  return inputNumbers.some((number) => number === "");
}

//스트라이크/볼 계산
function check_result(inputNumbers) {
  let strike = 0;
  let ball = 0;
  const checkedAnswer = [false, false, false];
  const checkedInput = [false, false, false];
//스트라이크
  for (let i = 0; i < 3; i++) {
    if (Number(inputNumbers[i]) === game.answer[i]) {
      strike++;
      checkedAnswer[i] = true;
      checkedInput[i] = true;
    }
  }
//볼
  for (let i = 0; i < 3; i++) {
    if (checkedInput[i]) continue;

    for (let j = 0; j < 3; j++) {
      if (checkedAnswer[j]) continue;

      if (Number(inputNumbers[i]) === game.answer[j]) {
        ball++;
        checkedAnswer[j] = true;
        break;
      }
    }
  }

  return { strike, ball };
}

//결과 화면에 추가
function add_result(inputNumbers, strike, ball) {
  const resultLine = document.createElement("div");
  const left = document.createElement("span");
  const center = document.createElement("span");
  const right = document.createElement("span");

  resultLine.className = "check-result";
  left.className = "left";
  center.textContent = ":";
  right.className = "right";

  left.textContent = inputNumbers.join("");

  if (strike === 0 && ball === 0) {
    right.innerHTML = '<span class="num-result out">O</span>';
  } else {
    right.innerHTML = `
      <span class="num-result strike">${strike} S</span>
      <span class="num-result ball">${ball} B</span>
    `;
  }

  resultLine.appendChild(left);
  resultLine.appendChild(center);
  resultLine.appendChild(right);
  resultsDiv.appendChild(resultLine);
}

//게임 끝
function finish_game(imageName) {
  game.isOver = true;
  resultImg.src = imageName;
  submitButton.disabled = true; //확인하기 버튼 비활성화
}

//버튼 활성화, 비활성화
function check_numbers() {
  if (game.isOver) return;

  const inputNumbers = get_input_numbers();

  //모든 input이 채워졌는지 확인, 빈 값이 있다면 확인하지 않고 input만 초기화
  if (has_empty_input(inputNumbers)) {
    clear_inputs();
    return;
  }

  const result = check_result(inputNumbers);
  game.attempts--;

  add_result(inputNumbers, result.strike, result.ball);
  update_attempts();
  clear_inputs();

  if (result.strike === 3) {
    finish_game("success.png");
    return;
  }

  if (game.attempts === 0) {
    finish_game("fail.png");
  }
}

init_game();