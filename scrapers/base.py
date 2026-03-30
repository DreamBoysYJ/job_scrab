"""
공통 스크래퍼 베이스 클래스
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import time
import logging
import requests
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """모든 스크래퍼의 베이스 클래스"""

    def __init__(self, keywords: list, config: Optional[dict] = None):
        """
        Args:
            keywords: 검색할 키워드 목록
            config: 추가 설정 (location, combination, exclude, experience 등)
        """
        self.keywords = keywords
        self.config = config or {}
        self.location = self.config.get("location", "한국")
        self.combination = self.config.get("combination", "OR")
        self.exclude = self.config.get("exclude", [])
        self.experience = self.config.get("experience", {})

        # HTTP 세션 설정
        self.session = requests.Session()
        self._setup_headers()

        # 요청 간 딜레이 (초)
        self.delay = 1.5

    def _setup_headers(self):
        """User-Agent 및 기본 헤더 설정"""
        try:
            ua = UserAgent()
            user_agent = ua.random
        except Exception:
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    def _delay(self):
        """요청 간 딜레이"""
        time.sleep(self.delay)

    def _get_timestamp(self) -> str:
        """현재 시각 반환"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _create_job_dict(
        self,
        title: str,
        company: str,
        url: str,
        location: str = "",
        experience: str = "",
        deadline: str = ""
    ) -> dict:
        """표준 채용공고 딕셔너리 생성"""
        return {
            "site": self.get_site_name(),
            "title": title,
            "company": company,
            "location": location,
            "experience": experience,
            "url": url,
            "deadline": deadline,
            "scraped_at": self._get_timestamp()
        }

    def _matches_keywords(self, text: str) -> bool:
        """텍스트가 키워드 조건에 맞는지 확인"""
        text_lower = text.lower()

        # 제외 키워드 체크
        for exclude_kw in self.exclude:
            if exclude_kw.lower() in text_lower:
                return False

        # 키워드 매칭
        if self.combination == "AND":
            return all(kw.lower() in text_lower for kw in self.keywords)
        else:  # OR
            return any(kw.lower() in text_lower for kw in self.keywords)

    @abstractmethod
    def search(self) -> list[dict]:
        """
        채용공고 검색 실행

        Returns:
            채용공고 딕셔너리 리스트
        """
        pass

    @abstractmethod
    def parse_job(self, data) -> dict:
        """
        채용공고 데이터 파싱

        Args:
            data: 파싱할 원본 데이터

        Returns:
            표준 형식의 채용공고 딕셔너리
        """
        pass

    @abstractmethod
    def get_site_name(self) -> str:
        """
        사이트명 반환

        Returns:
            사이트명 (예: "원티드", "잡코리아")
        """
        pass
