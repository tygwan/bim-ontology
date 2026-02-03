"""부하 테스트 스크립트.

동시 10명 사용자 시뮬레이션으로 API 응답 시간을 측정합니다.

사용법:
    # 서버 실행 후
    python scripts/load_test.py http://localhost:8001
"""

import asyncio
import sys
import time
import statistics

import httpx

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
CONCURRENT_USERS = 10
REQUESTS_PER_USER = 5

ENDPOINTS = [
    ("GET", "/health"),
    ("GET", "/api/statistics"),
    ("GET", "/api/buildings"),
    ("GET", "/api/storeys"),
    ("GET", "/api/elements?limit=10"),
    ("GET", "/api/elements?category=Pipe&limit=10"),
    ("GET", "/api/statistics/categories"),
    ("GET", "/api/hierarchy"),
    ("POST", "/api/sparql"),
]

SPARQL_BODY = {
    "query": """
        PREFIX bim: <http://example.org/bim-ontology/schema#>
        SELECT ?cat (COUNT(?e) AS ?num)
        WHERE { ?e bim:hasCategory ?cat }
        GROUP BY ?cat ORDER BY DESC(?num)
    """
}


async def make_request(client: httpx.AsyncClient, method: str, path: str) -> float:
    """단일 요청 실행, 응답 시간 반환 (ms)."""
    url = f"{BASE_URL}{path}"
    start = time.perf_counter()
    if method == "POST":
        r = await client.post(url, json=SPARQL_BODY)
    else:
        r = await client.get(url)
    elapsed = (time.perf_counter() - start) * 1000
    r.raise_for_status()
    return elapsed


async def user_session(user_id: int, results: list):
    """단일 사용자 세션: 모든 엔드포인트를 순서대로 호출."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        for _ in range(REQUESTS_PER_USER):
            for method, path in ENDPOINTS:
                try:
                    elapsed = await make_request(client, method, path)
                    results.append({
                        "user": user_id,
                        "endpoint": f"{method} {path.split('?')[0]}",
                        "time_ms": elapsed,
                        "status": "ok",
                    })
                except Exception as e:
                    results.append({
                        "user": user_id,
                        "endpoint": f"{method} {path.split('?')[0]}",
                        "time_ms": 0,
                        "status": f"error: {e}",
                    })


async def run_load_test():
    print(f"=== BIM Ontology 부하 테스트 ===")
    print(f"대상: {BASE_URL}")
    print(f"동시 사용자: {CONCURRENT_USERS}")
    print(f"사용자당 반복: {REQUESTS_PER_USER}")
    print(f"엔드포인트: {len(ENDPOINTS)}개")
    print(f"총 요청 수: {CONCURRENT_USERS * REQUESTS_PER_USER * len(ENDPOINTS)}")
    print()

    results = []
    start = time.perf_counter()

    tasks = [user_session(i, results) for i in range(CONCURRENT_USERS)]
    await asyncio.gather(*tasks)

    total_time = time.perf_counter() - start

    # 결과 분석
    ok_results = [r for r in results if r["status"] == "ok"]
    err_results = [r for r in results if r["status"] != "ok"]

    if ok_results:
        times = [r["time_ms"] for r in ok_results]
        print(f"--- 결과 ---")
        print(f"총 요청: {len(results)}")
        print(f"성공: {len(ok_results)}, 실패: {len(err_results)}")
        print(f"총 소요 시간: {total_time:.1f}초")
        print(f"처리량: {len(ok_results) / total_time:.1f} req/s")
        print()
        print(f"응답 시간 (ms):")
        print(f"  평균: {statistics.mean(times):.1f}")
        print(f"  중앙값: {statistics.median(times):.1f}")
        print(f"  P95: {sorted(times)[int(len(times) * 0.95)]:.1f}")
        print(f"  P99: {sorted(times)[int(len(times) * 0.99)]:.1f}")
        print(f"  최소: {min(times):.1f}")
        print(f"  최대: {max(times):.1f}")
        print()

        # 엔드포인트별 분석
        print(f"--- 엔드포인트별 ---")
        endpoints = {}
        for r in ok_results:
            ep = r["endpoint"]
            if ep not in endpoints:
                endpoints[ep] = []
            endpoints[ep].append(r["time_ms"])

        print(f"{'Endpoint':<35} {'Avg':>8} {'P95':>8} {'Max':>8}")
        print("-" * 65)
        for ep, t in sorted(endpoints.items()):
            avg = statistics.mean(t)
            p95 = sorted(t)[int(len(t) * 0.95)]
            mx = max(t)
            status = "PASS" if p95 < 2000 else "FAIL"
            print(f"{ep:<35} {avg:>7.1f} {p95:>7.1f} {mx:>7.1f}  {status}")

        # 성공 기준 판단
        p95_all = sorted(times)[int(len(times) * 0.95)]
        print()
        if p95_all < 2000 and len(err_results) == 0:
            print(f"PASS: P95={p95_all:.0f}ms < 2000ms, 에러 0건")
        else:
            print(f"FAIL: P95={p95_all:.0f}ms, 에러 {len(err_results)}건")

    if err_results:
        print(f"\n--- 에러 ---")
        for r in err_results[:5]:
            print(f"  User {r['user']}: {r['endpoint']} - {r['status']}")


if __name__ == "__main__":
    asyncio.run(run_load_test())
