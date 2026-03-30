#!/usr/bin/env python3
"""원티드 API 응답 디버깅"""
import requests

url = "https://www.wanted.co.kr/api/v4/jobs"
params = {
    "country": "kr",
    "job_sort": "job.latest_order",
    "years": "-1",
    "locations": "all",
    "keyword": "블록체인",
    "offset": 0,
    "limit": 5,
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept": "application/json",
    "Referer": "https://www.wanted.co.kr/",
}

response = requests.get(url, params=params, headers=headers)
print(f"Status: {response.status_code}")
print(f"URL: {response.url}")
print()

data = response.json()
jobs = data.get("data", [])

print(f"결과 수: {len(jobs)}")
print("=" * 60)

for job in jobs[:5]:
    print(f"ID: {job.get('id')}")
    print(f"제목: {job.get('position')}")
    print(f"회사: {job.get('company', {}).get('name')}")
    print("-" * 40)
