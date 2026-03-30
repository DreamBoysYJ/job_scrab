#!/usr/bin/env python3
"""원티드 검색 API 테스트"""
import requests

# 원티드 검색 API (v4/search)
url = "https://www.wanted.co.kr/api/v4/search"
params = {
    "query": "블록체인",
    "tab": "position",
    "country": "kr",
    "offset": 0,
    "limit": 5,
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept": "application/json",
    "Referer": "https://www.wanted.co.kr/search",
}

response = requests.get(url, params=params, headers=headers)
print(f"Status: {response.status_code}")
print(f"URL: {response.url}")
print()

if response.status_code == 200:
    import json
    data = response.json()
    inner = data.get("data", {})
    print(f"data 내부 키: {inner.keys()}")

    jobs = inner.get("jobs", [])
    print(f"jobs 수: {len(jobs)}")

    if jobs:
        for j in jobs[:5]:
            print(f"  - [{j.get('company', {}).get('name')}] {j.get('position')}")
            print(f"    ID: {j.get('id')}")
    else:
        print("\njobs 데이터 구조 확인:")
        print(json.dumps(inner.get("jobs"), indent=2, ensure_ascii=False))
else:
    print(f"Error: {response.text[:500]}")
