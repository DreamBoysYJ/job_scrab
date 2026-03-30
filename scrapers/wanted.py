"""
원티드 채용공고 스크래퍼
검색 API 기반으로 데이터 수집
"""
import logging
from typing import Optional

from .base import BaseScraper

logger = logging.getLogger(__name__)


class WantedScraper(BaseScraper):
    """원티드 스크래퍼"""

    SEARCH_URL = "https://www.wanted.co.kr/api/v4/search"
    JOB_URL = "https://www.wanted.co.kr/wd/{job_id}"

    def __init__(self, keywords: list, config: Optional[dict] = None):
        super().__init__(keywords, config)
        self.session.headers.update({
            "Accept": "application/json",
            "Referer": "https://www.wanted.co.kr/search",
        })

    def get_site_name(self) -> str:
        return "원티드"

    def search(self) -> list[dict]:
        """원티드 채용공고 검색"""
        all_jobs = []

        for keyword in self.keywords:
            try:
                jobs = self._search_keyword(keyword)
                all_jobs.extend(jobs)
                self._delay()
            except Exception as e:
                logger.error(f"원티드 검색 오류 (키워드: {keyword}): {e}")

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
        offset = 0
        limit = 20

        while True:
            params = {
                "query": keyword,
                "tab": "position",
                "country": "kr",
                "offset": offset,
                "limit": limit,
            }

            try:
                response = self.session.get(self.SEARCH_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"API 요청 실패: {e}")
                break

            inner_data = data.get("data", {})
            job_list = inner_data.get("jobs", [])

            if not job_list:
                break

            for job_data in job_list:
                job = self.parse_job(job_data)
                if job:
                    jobs.append(job)

            # 다음 페이지가 있는지 확인
            if len(job_list) < limit:
                break

            offset += limit

            # 최대 5페이지까지만 (100개)
            if offset >= 100:
                break

            self._delay()

        return jobs

    def parse_job(self, data: dict) -> Optional[dict]:
        """원티드 API 응답 파싱"""
        try:
            job_id = data.get("id")
            title = data.get("position", "")
            company = data.get("company", {}).get("name", "")
            location = data.get("address", {}).get("full_location", "")

            # 제외 키워드 체크
            full_text = f"{title} {company}"
            for exclude_kw in self.exclude:
                if exclude_kw.lower() in full_text.lower():
                    return None

            return self._create_job_dict(
                title=title,
                company=company,
                url=self.JOB_URL.format(job_id=job_id),
                location=location,
                experience="",
                deadline=""
            )
        except Exception as e:
            logger.error(f"파싱 오류: {e}")
            return None
