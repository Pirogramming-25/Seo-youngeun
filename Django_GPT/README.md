# Django GPT

Hugging Face `pipeline()`을 이용한 Django AI 웹 서비스입니다.

## 기능

| 기능 | URL | 접근 권한 |
| --- | --- | --- |
| 감정 분석 | `/sentiment/` | 비로그인 허용 |
| 문서 요약 | `/summarize/` | 로그인 필요 |
| 유해 표현 분석 | `/moderate/` | 로그인 필요 |

로그인 사용자의 성공한 실행 결과만 DB에 저장하며, 각 화면에는 현재 사용자의 해당 기능 기록을 최신 5개까지 표시합니다.

## 사용 모델

| 기능 | Model ID | Task | 입력 언어 | 출력 | 라이선스 |
| --- | --- | --- | --- | --- | --- |
| 감정 분석 | [`cardiffnlp/twitter-roberta-base-sentiment-latest`](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest) | `text-classification` | 영어 | `negative`, `neutral`, `positive`와 각 점수 | CC BY 4.0 |
| 문서 요약 | [`sshleifer/distilbart-cnn-6-6`](https://huggingface.co/sshleifer/distilbart-cnn-6-6) | `summarization` | 영어 | 영어 요약문, 원문·요약문 길이, 요약 비율 | Apache 2.0 |
| 유해 표현 분석 | [`unitary/toxic-bert`](https://huggingface.co/unitary/toxic-bert) | `text-classification` | 영어 | `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`와 각 점수 | Apache 2.0 |

## 실행 방법

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

PowerShell에서는 가상환경을 다음 명령으로 활성화합니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

브라우저에서 `http://127.0.0.1:8000/sentiment/`에 접속합니다. 모델은 각 기능을 처음 실행할 때 다운로드됩니다.

## 환경변수

`.env.example`을 `.env`로 복사하여 사용합니다.

```dotenv
DJANGO_SECRET_KEY=replace-with-a-long-random-value
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
HF_TOKEN=
```

사용 모델은 공개 모델이므로 일반적으로 `HF_TOKEN`이 필요하지 않습니다. 다운로드 제한이나 인증 오류가 발생할 때만 로컬 `.env`에 설정하며, `.env`와 실제 토큰은 GitHub에 업로드하지 않습니다.
