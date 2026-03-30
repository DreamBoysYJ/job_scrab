"""
사람인 채용공고 스크래퍼
웹 스크래핑 기반
"""
import logging
from typing import Optional
from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup

from .base import BaseScraper

logger = logging.getLogger(__name__)


class SaraminScraper(BaseScraper):
    """사람인 스크래퍼"""

    BASE_URL = "https://www.saramin.co.kr"
    SEARCH_URL = "https://www.saramin.co.kr/zf_user/search/recruit"

    def __init__(self, keywords: list, config: Optional[dict] = None):
        super().__init__(keywords, config)

    def get_site_name(self) -> str:
        return "사람인"

    def search(self) -> list[dict]:
        """사람인 채용공고 검색"""
        all_jobs = []

        for keyword in self.keywords:
            try:
                jobs = self._search_keyword(keyword)
                all_jobs.extend(jobs)
                self._delay()
            except Exception as e:
                logger.error(f"사람인 검색 오류 (키워드: {keyword}): {e}")

        # 중복 제거 (URL 기준)
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                unique_jobs.append(job)

        return unique_jobs

    def _search_keyword(self, keyword: str) -> list[dict]:
        """특정 키워드로 검색"""
        jobs = []

        for page in range(1, 4):  # 최대 3페이지
            params = {
                "searchType": "search",
                "searchword": keyword,
                "recruitPage": page,
                "recruitSort": "relation",
                "recruitPageCount": 40,
            }

            url = f"{self.SEARCH_URL}?{urlencode(params)}"

            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
            except Exception as e:
                logger.error(f"페이지 요청 실패: {e}")
                break

            soup = BeautifulSoup(response.text, "html.parser")

            # 채용공고 목록 찾기
            job_list = soup.select("div.item_recruit")

            if not job_list:
                break

            for job_elem in job_list:
                job = self._parse_job_element(job_elem)
                if job:
                    jobs.append(job)

            self._delay()

        return jobs

    def _parse_job_element(self, elem) -> Optional[dict]:
        """HTML 요소에서 채용공고 파싱"""
        try:
            # 제목과 링크
            title_elem = elem.select_one("h2.job_tit a")
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)
            href = title_elem.get("href", "")
            url = urljoin(self.BASE_URL, href)

            # 회사명
            company_elem = elem.select_one("strong.corp_name a")
            if not company_elem:
                company_elem = elem.select_one("div.area_corp strong.corp_name")
            company = company_elem.get_text(strip=True) if company_elem else ""

            # 조건 정보 (근무지, 경력, 학력 등)
            conditions = elem.select("div.job_condition span")

            location = ""
            experience = ""

            for cond in conditions:
                text = cond.get_text(strip=True)
                # 근무지는 보통 첫 번째
                if not location and any(loc in text for loc in ["서울", "경기", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주", "전국"]):
                    location = text
                # 경력
                elif "경력" in text or "신입" in text:
                    experience = text

            # 마감일
            deadline_elem = elem.select_one("span.job_date span.date")
            if not deadline_elem:
                deadline_elem = elem.select_one("div.job_date span.date")
            deadline = deadline_elem.get_text(strip=True) if deadline_elem else ""

            # 제외 키워드 체크
            full_text = f"{title} {company} {experience}"
            for exclude_kw in self.exclude:
                if exclude_kw.lower() in full_text.lower():
                    return None

            return self._create_job_dict(
                title=title,
                company=company,
                url=url,
                location=location,
                experience=experience,
                deadline=deadline
            )
        except Exception as e:
            logger.error(f"파싱 오류: {e}")
            return None

    def parse_job(self, data) -> dict:
        """BaseScraper 인터페이스 구현"""
        return self._parse_job_element(data)
