#!/usr/bin/env python3
"""
채용공고 스크래핑 메인 실행 파일

사용법:
    python main.py                    # 전체 실행
    python main.py --sites wanted saramin  # 특정 사이트만
    python main.py --no-telegram      # 텔레그램 알림 없이
    python main.py --dry-run          # 스크래핑만 (저장/알림 X)
"""
import argparse
import asyncio
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from scrapers import SCRAPERS, get_all_scrapers
from utils import (
    load_keywords,
    save_to_excel,
    get_summary_by_site,
    send_notification,
    get_credentials_from_env,
)


def setup_logging(verbose: bool = False):
    """로깅 설정"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_scraper(scraper_class, keywords: list, config: dict) -> list[dict]:
    """단일 스크래퍼 실행"""
    logger = logging.getLogger(__name__)
    site_name = scraper_class.__name__.replace("Scraper", "")

    try:
        logger.info(f"[{site_name}] 스크래핑 시작...")
        scraper = scraper_class(keywords=keywords, config=config)
        jobs = scraper.search()
        logger.info(f"[{site_name}] 완료: {len(jobs)}건 수집")
        return jobs
    except Exception as e:
        logger.error(f"[{site_name}] 스크래핑 실패: {e}")
        return []


def run_all_scrapers(
    scraper_classes: list,
    keywords: list,
    config: dict,
    max_workers: int = 3
) -> list[dict]:
    """모든 스크래퍼를 병렬로 실행"""
    logger = logging.getLogger(__name__)
    all_jobs = []

    logger.info(f"총 {len(scraper_classes)}개 사이트 스크래핑 시작")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_scraper = {
            executor.submit(run_scraper, sc, keywords, config): sc
            for sc in scraper_classes
        }

        for future in as_completed(future_to_scraper):
            scraper = future_to_scraper[future]
            try:
                jobs = future.result()
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"{scraper.__name__} 오류: {e}")

    return all_jobs


def remove_duplicates(jobs: list[dict]) -> list[dict]:
    """URL 기준 중복 제거"""
    seen_urls = set()
    unique_jobs = []

    for job in jobs:
        url = job.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_jobs.append(job)

    return unique_jobs


def print_summary(jobs: list[dict]):
    """결과 요약 출력"""
    logger = logging.getLogger(__name__)
    summary = get_summary_by_site(jobs)

    logger.info("=" * 50)
    logger.info(f"스크래핑 완료: 총 {len(jobs)}건")
    logger.info("-" * 50)
    for site, count in sorted(summary.items(), key=lambda x: -x[1]):
        logger.info(f"  {site}: {count}건")
    logger.info("=" * 50)


async def main_async(args):
    """메인 비동기 실행 함수"""
    logger = logging.getLogger(__name__)

    # 1. 키워드 설정 로드
    logger.info("키워드 설정 로드 중...")
    config = load_keywords()
    keywords = config.get("keywords", [])

    if not keywords:
        logger.error("검색할 키워드가 없습니다. config/keywords.yaml을 확인하세요.")
        return 1

    logger.info(f"키워드: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")

    # 2. 스크래퍼 선택
    if args.sites:
        scraper_classes = []
        for site in args.sites:
            site_lower = site.lower()
            if site_lower in SCRAPERS:
                scraper_classes.append(SCRAPERS[site_lower])
            else:
                logger.warning(f"알 수 없는 사이트: {site}")
        if not scraper_classes:
            logger.error("유효한 사이트가 없습니다.")
            return 1
    else:
        scraper_classes = get_all_scrapers()

    # 3. 스크래핑 실행
    jobs = run_all_scrapers(
        scraper_classes=scraper_classes,
        keywords=keywords,
        config=config,
        max_workers=args.workers
    )

    # 4. 중복 제거
    jobs = remove_duplicates(jobs)

    # 5. 결과 요약 출력
    print_summary(jobs)

    if args.dry_run:
        logger.info("--dry-run 모드: 저장 및 알림을 건너뜁니다.")
        return 0

    if not jobs:
        logger.warning("수집된 채용공고가 없습니다.")

    # 6. 엑셀 저장
    excel_path = ""
    if not args.no_excel:
        excel_path = save_to_excel(jobs)
        if excel_path:
            logger.info(f"엑셀 저장 완료: {excel_path}")

    # 7. 텔레그램 알림
    if not args.no_telegram:
        bot_token, chat_id = get_credentials_from_env()

        if bot_token and chat_id:
            success = await send_notification(
                bot_token=bot_token,
                chat_id=chat_id,
                jobs=jobs,
                excel_path=excel_path,
                keywords=keywords,
                combination=config.get("combination", "OR")
            )
            if success:
                logger.info("텔레그램 알림 전송 완료")
            else:
                logger.error("텔레그램 알림 전송 실패")
        else:
            logger.warning(
                "텔레그램 환경변수가 설정되지 않았습니다. "
                "TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID를 설정하세요."
            )

    return 0


def main():
    """CLI 진입점"""
    parser = argparse.ArgumentParser(
        description="채용공고 스크래핑 자동화",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python main.py                          # 전체 사이트 스크래핑
  python main.py --sites wanted saramin   # 특정 사이트만
  python main.py --no-telegram            # 텔레그램 알림 없이
  python main.py --dry-run                # 테스트 모드 (저장/알림 X)
  python main.py -v                       # 상세 로그 출력

지원 사이트: wanted, jobkorea, saramin, catch, jasoseol, rocketpunch
        """
    )

    parser.add_argument(
        "--sites", "-s",
        nargs="+",
        help="스크래핑할 사이트 목록 (기본: 전체)"
    )
    parser.add_argument(
        "--no-telegram",
        action="store_true",
        help="텔레그램 알림 비활성화"
    )
    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="엑셀 저장 비활성화"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="스크래핑만 실행 (저장/알림 없이)"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=3,
        help="병렬 작업자 수 (기본: 3)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="상세 로그 출력"
    )

    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    logger.info(f"채용공고 스크래핑 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        exit_code = asyncio.run(main_async(args))
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
        exit_code = 130
    except Exception as e:
        logger.exception(f"예기치 않은 오류: {e}")
        exit_code = 1

    logger.info("완료")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
