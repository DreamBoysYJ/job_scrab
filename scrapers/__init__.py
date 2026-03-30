# scrapers 패키지

from .base import BaseScraper
from .wanted import WantedScraper
from .jobkorea import JobKoreaScraper
from .saramin import SaraminScraper
from .catch import CatchScraper
from .jasoseol import JasoseolScraper
from .rocketpunch import RocketPunchScraper

__all__ = [
    "BaseScraper",
    "WantedScraper",
    "JobKoreaScraper",
    "SaraminScraper",
    "CatchScraper",
    "JasoseolScraper",
    "RocketPunchScraper",
]

# 편의를 위한 스크래퍼 목록
SCRAPERS = {
    "wanted": WantedScraper,
    "jobkorea": JobKoreaScraper,
    "saramin": SaraminScraper,
    "catch": CatchScraper,
    "jasoseol": JasoseolScraper,
    "rocketpunch": RocketPunchScraper,
}


def get_all_scrapers():
    """모든 스크래퍼 클래스 반환"""
    return list(SCRAPERS.values())


def get_scraper(name: str):
    """이름으로 스크래퍼 클래스 반환"""
    return SCRAPERS.get(name.lower())
