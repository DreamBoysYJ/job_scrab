#!/usr/bin/env python3
"""
스크래핑 결과 검증 스크립트
엑셀 파일의 채용공고가 키워드와 실제로 관련 있는지 확인
"""
import sys
from pathlib import Path

import pandas as pd

from utils import load_keywords


def verify_excel(excel_path: str):
    """엑셀 파일의 채용공고 검증"""

    # 키워드 로드
    config = load_keywords()
    keywords = [kw.lower() for kw in config.get("keywords", [])]

    if not keywords:
        print("키워드가 설정되지 않았습니다.")
        return

    print(f"검증 키워드: {keywords}")
    print("=" * 60)

    # 엑셀 읽기
    df = pd.read_excel(excel_path)
    total = len(df)

    matched = []
    not_matched = []

    for idx, row in df.iterrows():
        title = str(row.get("공고제목", "")).lower()
        company = str(row.get("회사명", "")).lower()

        # 키워드 매칭 확인
        found = False
        for kw in keywords:
            if kw in title or kw in company:
                found = True
                break

        if found:
            matched.append(row)
        else:
            not_matched.append(row)

    # 결과 출력
    print(f"\n총 {total}건 중:")
    print(f"  - 키워드 매칭: {len(matched)}건")
    print(f"  - 키워드 미매칭: {len(not_matched)}건")
    print(f"  - 매칭률: {len(matched)/total*100:.1f}%")

    if not_matched:
        print("\n" + "=" * 60)
        print("키워드 미매칭 공고 목록:")
        print("-" * 60)
        for row in not_matched:
            print(f"  [{row.get('회사명', '')}] {row.get('공고제목', '')}")

    print("\n" + "=" * 60)
    if not_matched:
        print(f"결과: {len(not_matched)}건이 키워드와 직접 매칭되지 않음")
        print("(API 검색 결과이므로 내부적으로 관련성이 있을 수 있음)")
    else:
        print("결과: 모든 공고가 키워드와 매칭됨")


if __name__ == "__main__":
    # 최신 엑셀 파일 찾기
    output_dir = Path("output")
    excel_files = sorted(output_dir.glob("jobs_*.xlsx"), reverse=True)

    if not excel_files:
        print("엑셀 파일이 없습니다.")
        sys.exit(1)

    latest = excel_files[0]
    print(f"검증 파일: {latest}\n")

    verify_excel(str(latest))
