# 채용공고 스크래핑 자동화 프로젝트

## 개요
매일 아침 GitHub Actions로 채용공고를 스크래핑하여 텔레그램으로 알림 받는 시스템

## 기술 스택
- **언어**: Python 3.11+
- **스크래핑**: requests, BeautifulSoup4, Selenium
- **데이터**: pandas, openpyxl
- **알림**: python-telegram-bot
- **스케줄링**: GitHub Actions (cron)

## 프로젝트 구조

```
job_scrab/
├── config/           # 설정 파일
├── scrapers/         # 사이트별 스크래퍼
├── utils/            # 유틸리티 모듈
├── output/           # 엑셀 출력 (gitignore)
├── .github/workflows # GitHub Actions
├── main.py           # 메인 실행
└── requirements.txt  # 의존성
```

## 폴더별 상세 문서

| 폴더 | 역할 | 문서 |
|------|------|------|
| config | 키워드 및 설정 관리 | [config/CLAUDE.md](config/CLAUDE.md) |
| scrapers | 채용 사이트별 스크래퍼 | [scrapers/CLAUDE.md](scrapers/CLAUDE.md) |
| utils | 공통 유틸리티 (엑셀, 텔레그램) | [utils/CLAUDE.md](utils/CLAUDE.md) |
| .github/workflows | GitHub Actions 설정 | [.github/workflows/CLAUDE.md](.github/workflows/CLAUDE.md) |

## 대상 사이트

| 사이트 | 방식 | 구현 난이도 |
|--------|------|-------------|
| 원티드 | API | ⭐ 쉬움 |
| 잡코리아 | 웹 스크래핑 | ⭐⭐ 보통 |
| 사람인 | 웹 스크래핑 | ⭐⭐ 보통 |
| 캐치 | 웹 스크래핑 | ⭐⭐ 보통 |
| 자소설닷컴 | 웹 스크래핑 | ⭐⭐ 보통 |
| 로켓펀치 | 웹 스크래핑 | ⭐⭐ 보통 |
| 링크드인 | 제한적 | ⭐⭐⭐ 어려움 |

## 빠른 시작

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 키워드 설정
`config/keywords.yaml` 파일 수정

### 3. 환경변수 설정
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

### 4. 실행
```bash
python main.py
```

## 구현 진행 상황

👉 [PROGRESS.md](PROGRESS.md) 참조

## 주의사항
- 각 사이트 robots.txt 및 이용약관 확인
- 과도한 요청 시 IP 차단 가능 → 요청 간 딜레이 필수
- 링크드인은 스크래핑 제한이 심함
