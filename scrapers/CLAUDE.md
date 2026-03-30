# scrapers 폴더

## 역할
각 채용 사이트별 스크래퍼 모듈을 관리하는 폴더

## 파일 구조

### base.py
모든 스크래퍼의 공통 베이스 클래스

```python
class BaseScraper:
    def __init__(self, keywords: list)
    def search(self) -> list[dict]      # 검색 실행
    def parse_job(self, data) -> dict   # 공고 파싱
    def get_site_name(self) -> str      # 사이트명 반환
```

### 반환 데이터 형식
각 스크래퍼는 다음 형식의 딕셔너리 리스트를 반환:

```python
{
    "site": str,           # 사이트명 (원티드, 잡코리아 등)
    "title": str,          # 공고 제목
    "company": str,        # 회사명
    "location": str,       # 근무지
    "experience": str,     # 경력 요구사항
    "url": str,            # 공고 상세 URL
    "deadline": str,       # 마감일 (있는 경우)
    "scraped_at": str      # 스크래핑 시각
}
```

## 스크래퍼 목록

| 파일 | 사이트 | 방식 | 난이도 |
|------|--------|------|--------|
| wanted.py | 원티드 | API | 쉬움 |
| jobkorea.py | 잡코리아 | 웹 스크래핑 | 보통 |
| saramin.py | 사람인 | 웹 스크래핑 | 보통 |
| catch.py | 캐치 | 웹 스크래핑 | 보통 |
| jasoseol.py | 자소설닷컴 | 웹 스크래핑 | 보통 |
| rocketpunch.py | 로켓펀치 | 웹 스크래핑 | 보통 |
| linkedin.py | 링크드인 | 제한적 | 어려움 |

## 구현 가이드

### 새 스크래퍼 추가 시
1. `BaseScraper`를 상속받아 구현
2. `search()` 메서드 필수 구현
3. `__init__.py`에 import 추가

### 주의사항
- 요청 간 딜레이 필수 (1-3초 권장)
- User-Agent 헤더 설정
- 에러 처리 및 로깅
- robots.txt 확인
