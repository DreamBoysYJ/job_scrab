"""
엑셀 파일 저장 유틸리티
"""
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def save_to_excel(jobs: list[dict], filename: str = None) -> str:
    """
    채용공고 목록을 엑셀 파일로 저장

    Args:
        jobs: 채용공고 딕셔너리 리스트
        filename: 저장할 파일명 (기본값: output/jobs_YYYYMMDD.xlsx)

    Returns:
        저장된 파일 경로
    """
    if not jobs:
        logger.warning("저장할 채용공고가 없습니다")
        return ""

    # output 폴더 생성
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # 파일명 설정
    if filename is None:
        today = datetime.now().strftime("%Y%m%d")
        filename = f"jobs_{today}.xlsx"

    filepath = output_dir / filename

    # 컬럼 순서 및 한글명 매핑
    column_mapping = {
        "site": "사이트",
        "title": "공고제목",
        "company": "회사명",
        "location": "근무지",
        "experience": "경력",
        "deadline": "마감일",
        "url": "링크",
        "scraped_at": "수집시각"
    }

    try:
        df = pd.DataFrame(jobs)

        # 존재하는 컬럼만 순서대로 정렬
        ordered_columns = [col for col in column_mapping.keys() if col in df.columns]
        df = df[ordered_columns]

        # 컬럼명 한글로 변경
        df = df.rename(columns=column_mapping)

        # 엑셀 저장 (openpyxl 엔진 사용)
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="채용공고")

            # 컬럼 너비 자동 조정
            worksheet = writer.sheets["채용공고"]
            for idx, col in enumerate(df.columns, 1):
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                )
                # 한글은 2배 너비 적용
                adjusted_width = min(max_length * 1.5 + 2, 50)
                worksheet.column_dimensions[chr(64 + idx)].width = adjusted_width

        logger.info(f"엑셀 저장 완료: {filepath} ({len(jobs)}건)")
        return str(filepath)

    except Exception as e:
        logger.error(f"엑셀 저장 실패: {e}")
        return ""


def get_summary_by_site(jobs: list[dict]) -> dict[str, int]:
    """
    사이트별 채용공고 수 집계

    Args:
        jobs: 채용공고 딕셔너리 리스트

    Returns:
        {사이트명: 공고수} 딕셔너리
    """
    summary = {}
    for job in jobs:
        site = job.get("site", "기타")
        summary[site] = summary.get(site, 0) + 1
    return summary
