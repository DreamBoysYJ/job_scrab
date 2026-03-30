# .github/workflows 폴더

## 역할
GitHub Actions 워크플로우 설정 파일 관리

## 파일 구조

### daily_scrape.yml
매일 자동으로 채용공고를 스크래핑하는 워크플로우

## 스케줄
- **실행 시간**: 매일 오전 9시 (KST)
- **cron 표현식**: `0 0 * * *` (UTC 기준 자정 = KST 9시)

## 워크플로우 단계
1. 저장소 체크아웃
2. Python 환경 설정
3. 의존성 설치
4. 스크래핑 실행
5. 텔레그램 알림 전송

## GitHub Secrets 설정

### 필수 시크릿
저장소 Settings > Secrets and variables > Actions에서 설정:

| 이름 | 설명 | 예시 |
|------|------|------|
| `TELEGRAM_BOT_TOKEN` | 텔레그램 봇 토큰 | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | 알림 받을 채팅방 ID | `123456789` |

### 텔레그램 봇 생성 방법
1. 텔레그램에서 @BotFather 검색
2. `/newbot` 명령어 입력
3. 봇 이름과 username 설정
4. 발급된 토큰 복사

### 채팅방 ID 확인 방법
1. 생성한 봇과 대화 시작
2. `https://api.telegram.org/bot<TOKEN>/getUpdates` 접속
3. 응답에서 `chat.id` 값 확인

## 수동 실행
Actions 탭 > "Daily Job Scraping" > "Run workflow" 버튼

## 주의사항
- Secrets는 저장소 소유자만 설정 가능
- 워크플로우 실행 로그에서 토큰이 노출되지 않도록 주의
- 월간 실행 시간 제한 확인 (무료: 2000분/월)
