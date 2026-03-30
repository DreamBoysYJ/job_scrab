"""
텔레그램 알림 전송 유틸리티
"""
import os
import logging
from datetime import datetime
from pathlib import Path

from telegram import Bot
from telegram.error import TelegramError
from telegram.request import HTTPXRequest

logger = logging.getLogger(__name__)


def _build_message(jobs: list[dict], keywords: list[str] = None, combination: str = "OR") -> str:
    """
    텔레그램 알림 메시지 생성

    Args:
        jobs: 채용공고 딕셔너리 리스트
        keywords: 검색에 사용된 키워드 목록
        combination: 키워드 조합 방식

    Returns:
        포맷팅된 메시지 문자열
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # 사이트별 집계
    site_counts = {}
    for job in jobs:
        site = job.get("site", "기타")
        site_counts[site] = site_counts.get(site, 0) + 1

    # 메시지 구성
    lines = [f"📢 오늘의 채용공고 ({today})", ""]

    # 키워드 정보
    if keywords:
        keyword_str = f" {combination} ".join(keywords[:5])  # 최대 5개만 표시
        if len(keywords) > 5:
            keyword_str += f" 외 {len(keywords) - 5}개"
        lines.append(f"🔍 키워드: {keyword_str}")

    lines.append(f"📊 총 {len(jobs)}건 발견")
    lines.append("")

    # 사이트별 현황
    for site, count in sorted(site_counts.items(), key=lambda x: -x[1]):
        lines.append(f"[{site}] {count}건")

    lines.append("")
    lines.append("📎 상세 내용은 첨부 엑셀 참고")

    return "\n".join(lines)


async def send_notification(
    bot_token: str,
    chat_id: str,
    jobs: list[dict],
    excel_path: str = None,
    keywords: list[str] = None,
    combination: str = "OR"
) -> bool:
    """
    텔레그램으로 스크래핑 결과 알림 전송

    Args:
        bot_token: 텔레그램 봇 토큰
        chat_id: 수신할 채팅방 ID
        jobs: 채용공고 목록
        excel_path: 첨부할 엑셀 파일 경로
        keywords: 검색에 사용된 키워드 목록
        combination: 키워드 조합 방식

    Returns:
        전송 성공 여부
    """
    if not bot_token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다")
        return False

    try:
        # 타임아웃 설정 (GitHub Actions 환경에서 필요)
        request = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0)
        bot = Bot(token=bot_token, request=request)

        # 결과가 없는 경우
        if not jobs:
            today = datetime.now().strftime("%Y-%m-%d")
            message = f"📢 오늘의 채용공고 ({today})\n\n검색된 채용공고가 없습니다."
            await bot.send_message(chat_id=chat_id, text=message)
            logger.info("빈 결과 알림 전송 완료")
            return True

        # 메시지 전송
        message = _build_message(jobs, keywords, combination)
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info("텔레그램 메시지 전송 완료")

        # 엑셀 파일 첨부
        if excel_path and Path(excel_path).exists():
            with open(excel_path, "rb") as f:
                await bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    filename=Path(excel_path).name,
                    caption="📎 채용공고 상세 목록"
                )
            logger.info(f"엑셀 파일 전송 완료: {excel_path}")

        return True

    except TelegramError as e:
        logger.error(f"텔레그램 전송 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"알림 전송 실패: {e}")
        return False


def get_credentials_from_env() -> tuple[str, str]:
    """
    환경변수에서 텔레그램 자격증명 읽기

    Returns:
        (bot_token, chat_id) 튜플
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    return bot_token, chat_id
