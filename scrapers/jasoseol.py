"""
자소설닷컴 채용공고 스크래퍼
웹 스크래핑 기반
"""
import logging
from typing import Optional
from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup

from .base import BaseScraper

logger = logging.getLogger(__name__)


class JasoseolScraper(BaseScraper):
    """자소설닷컴 스크래퍼"""

    BASE_URL = "https://jasoseol.com"
    SEARCH_URL = "https://jasoseol.com/recruit"

    def __init__(self, keywords: list, config: Optional[dict] = None):
        super().__init__(keywords, config)

    def get_site_name(self) -> str:
        return "자소설닷컴"

    def search(self) -> list[dict]:
        """자소설닷컴 채용공고 검색"""
        all_jobs = []

        for keyword in self.keywords:
            try:
                jobs = self._search_keyword(keyword)
                all_jobs.extend(jobs)
                self._delay()
            except Exception as e:
                logger.error(f"자소설닷컴 검색 오류 (키워드: {keyword}): {e}")

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
                "q": keyword,
                "page": page,
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
            job_list = soup.select("div.recruit-item")
            if not job_list:
                job_list = soup.select("li.recruit-card")
            if not job_list:
                job_list = soup.select("article.job-item")

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
            title_elem = elem.select_one("a.recruit-title")
            if not title_elem:
                title_elem = elem.select_one("h3 a")
            if not title_elem:
                title_elem = elem.select_one("a[href*='recruit']")

            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)
            href = title_elem.get("href", "")
            url = urljoin(self.BASE_URL, href)

            # 회사명
            company_elem = elem.select_one("span.company-name")
            if not company_elem:
                company_elem = elem.select_one("p.company")
            if not company_elem:
                company_elem = elem.select_one("div.company")
            company = company_elem.get_text(strip=True) if company_elem else ""

            # 근무지
            location_elem = elem.select_one("span.location")
            if not location_elem:
                location_elem = elem.select_one("span.area")
            location = location_elem.get_text(strip=True) if location_elem else ""

            # 경력
            exp_elem = elem.select_one("span.career")
            if not exp_elem:
                exp_elem = elem.select_one("span.experience")
            experience = exp_elem.get_text(strip=True) if exp_elem else ""

            # 마감일
            deadline_elem = elem.select_one("span.deadline")
            if not deadline_elem:
                deadline_elem = elem.select_one("span.d-day")
            if not deadline_elem:
                deadline_elem = elem.select_one("span.date")
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
