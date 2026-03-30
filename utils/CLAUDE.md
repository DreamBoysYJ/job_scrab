# utils 폴더

## 역할
공통 유틸리티 모듈을 관리하는 폴더

## 파일 구조

### keywords.py
키워드 설정 파일 읽기

```python
def load_keywords(path: str = "config/keywords.yaml") -> dict
    """
    YAML 파일에서 키워드 설정을 읽어옴

    Returns:
        {
            "keywords": list,
            "location": str,
            "combination": str,
            "exclude": list,
            "experience": dict
        }
    """
```

### excel.py
스크래핑 결과를 엑셀 파일로 저장

```python
def save_to_excel(jobs: list[dict], filename: str = None) -> str
    """
    채용공고 목록을 엑셀 파일로 저장

    Args:
        jobs: 채용공고 딕셔너리 리스트
        filename: 저장할 파일명 (기본값: output/jobs_YYYYMMDD.xlsx)

    Returns:
        저장된 파일 경로
    """
```

### telegram.py
텔레그램 알림 전송

```python
async def send_notification(
    bot_token: str,
    chat_id: str,
    jobs: list[dict],
    excel_path: str = None
) -> bool
    """
    텔레그램으로 스크래핑 결과 알림 전송

    Args:
        bot_token: 텔레그램 봇 토큰
        chat_id: 수신할 채팅방 ID
        jobs: 채용공고 목록
        excel_path: 첨부할 엑셀 파일 경로

    Returns:
        전송 성공 여부
    """
```

## 환경변수

텔레그램 알림을 위해 필요한 환경변수:
- `TELEGRAM_BOT_TOKEN`: 봇 토큰 (@BotFather에서 발급)
- `TELEGRAM_CHAT_ID`: 알림 받을 채팅방 ID

## 알림 메시지 형식

```
📢 오늘의 채용공고 (2024-03-30)

🔍 키워드: 블록체인 AND 백엔드
📊 총 25건 발견

[원티드] 5건
[잡코리아] 4건
[사람인] 6건
...

📎 상세 내용은 첨부 엑셀 참고
```
