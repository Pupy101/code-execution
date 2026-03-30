"""
Stress test: concurrent real-code execution across top-5 languages.

Targets a LIVE service (not TestClient). Set BASE_URL env var to override.
Default: http://localhost:8000

Run:
    pytest tests/test_stress.py -v -s
    CONCURRENCY=20 pytest tests/test_stress.py -v -s
"""

import asyncio
import os
import statistics
import time
from dataclasses import dataclass, field

import httpx
import pytest

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
CONCURRENCY = int(os.environ.get("CONCURRENCY", "10"))
TIMEOUT = int(os.environ.get("EXEC_TIMEOUT", "30"))

# ---------------------------------------------------------------------------
# Real workloads per language
# ---------------------------------------------------------------------------

PAYLOADS: dict[str, dict] = {
    "python": {
        "lang": "python",
        "code": """\
import sys

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left  = [x for x in arr if x < pivot]
    mid   = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + mid + quicksort(right)

def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

data  = list(range(500, 0, -1))
sorted_data = quicksort(data)
assert sorted_data == list(range(1, 501)), "sort failed"

primes = sieve(1000)
assert len(primes) == 168, f"expected 168 primes, got {len(primes)}"
print(f"OK: sorted 500 numbers, found {len(primes)} primes up to 1000")
""",
        "expected_substr": "OK: sorted 500 numbers",
    },
    "cpp": {
        "lang": "cpp",
        "code": """\
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

std::vector<int> merge_sort(std::vector<int> arr) {
    if (arr.size() <= 1) return arr;
    size_t mid = arr.size() / 2;
    auto left  = merge_sort(std::vector<int>(arr.begin(), arr.begin() + mid));
    auto right = merge_sort(std::vector<int>(arr.begin() + mid, arr.end()));
    std::vector<int> result;
    size_t i = 0, j = 0;
    while (i < left.size() && j < right.size())
        result.push_back(left[i] < right[j] ? left[i++] : right[j++]);
    while (i < left.size())  result.push_back(left[i++]);
    while (j < right.size()) result.push_back(right[j++]);
    return result;
}

long long fib(int n) {
    if (n <= 1) return n;
    long long a = 0, b = 1;
    for (int i = 2; i <= n; i++) { long long c = a + b; a = b; b = c; }
    return b;
}

int main() {
    std::vector<int> data;
    for (int i = 500; i >= 1; i--) data.push_back(i);
    auto sorted = merge_sort(data);
    for (int i = 0; i < (int)sorted.size(); i++)
        assert(sorted[i] == i + 1);

    long long f40 = fib(40);
    assert(f40 == 102334155LL);

    std::cout << "OK: sorted 500 numbers, fib(40)=" << f40 << std::endl;
    return 0;
}
""",
        "expected_substr": "OK: sorted 500 numbers",
    },
    "java": {
        "lang": "java",
        "code": """\
import java.util.*;

public class Main {
    static int[] mergeSort(int[] arr) {
        if (arr.length <= 1) return arr;
        int mid = arr.length / 2;
        int[] left  = mergeSort(Arrays.copyOfRange(arr, 0, mid));
        int[] right = mergeSort(Arrays.copyOfRange(arr, mid, arr.length));
        int[] result = new int[arr.length];
        int i = 0, j = 0, k = 0;
        while (i < left.length && j < right.length)
            result[k++] = left[i] < right[j] ? left[i++] : right[j++];
        while (i < left.length)  result[k++] = left[i++];
        while (j < right.length) result[k++] = right[j++];
        return result;
    }

    static long fibonacci(int n) {
        if (n <= 1) return n;
        long a = 0, b = 1;
        for (int i = 2; i <= n; i++) { long c = a + b; a = b; b = c; }
        return b;
    }

    public static void main(String[] args) {
        int[] data = new int[500];
        for (int i = 0; i < 500; i++) data[i] = 500 - i;
        int[] sorted = mergeSort(data);
        for (int i = 0; i < sorted.length; i++)
            assert sorted[i] == i + 1 : "sort error at " + i;

        long f45 = fibonacci(45);
        assert f45 == 1134903170L : "fib(45) wrong: " + f45;

        System.out.println("OK: sorted 500 numbers, fib(45)=" + f45);
    }
}
""",
        "expected_substr": "OK: sorted 500 numbers",
    },
    "go": {
        "lang": "go",
        "code": """\
package main

import "fmt"

func sieve(n int) []int {
    isPrime := make([]bool, n+1)
    for i := 2; i <= n; i++ { isPrime[i] = true }
    for i := 2; i*i <= n; i++ {
        if isPrime[i] {
            for j := i * i; j <= n; j += i { isPrime[j] = false }
        }
    }
    primes := []int{}
    for i := 2; i <= n; i++ {
        if isPrime[i] { primes = append(primes, i) }
    }
    return primes
}

func mergeSort(arr []int) []int {
    if len(arr) <= 1 { return arr }
    mid := len(arr) / 2
    left  := mergeSort(arr[:mid])
    right := mergeSort(arr[mid:])
    result := make([]int, 0, len(arr))
    i, j := 0, 0
    for i < len(left) && j < len(right) {
        if left[i] < right[j] { result = append(result, left[i]); i++ } else { result = append(result, right[j]); j++ }
    }
    result = append(result, left[i:]...)
    result = append(result, right[j:]...)
    return result
}

func main() {
    data := make([]int, 500)
    for i := range data { data[i] = 500 - i }
    sorted := mergeSort(data)
    for i, v := range sorted {
        if v != i+1 { panic(fmt.Sprintf("sort error at %d: got %d", i, v)) }
    }
    primes := sieve(10000)
    if len(primes) != 1229 { panic(fmt.Sprintf("expected 1229 primes, got %d", len(primes))) }
    fmt.Printf("OK: sorted 500 numbers, found %d primes up to 10000\\n", len(primes))
}
""",
        "expected_substr": "OK: sorted 500 numbers",
    },
    "nodejs": {
        "lang": "nodejs",
        "code": """\
function matMul(A, B, n) {
    const C = Array.from({length: n}, () => new Array(n).fill(0));
    for (let i = 0; i < n; i++)
        for (let k = 0; k < n; k++)
            for (let j = 0; j < n; j++)
                C[i][j] += A[i][k] * B[k][j];
    return C;
}

function identity(n) {
    return Array.from({length: n}, (_, i) => Array.from({length: n}, (_, j) => i === j ? 1 : 0));
}

const n = 50;
const I = identity(n);
const A = Array.from({length: n}, () => Array.from({length: n}, () => Math.floor(Math.random() * 10)));
const result = matMul(A, I, n);  // A * I == A

let ok = true;
for (let i = 0; i < n; i++)
    for (let j = 0; j < n; j++)
        if (result[i][j] !== A[i][j]) { ok = false; break; }

// also check fibonacci
function fib(n) {
    let [a, b] = [0n, 1n];
    for (let i = 0; i < n; i++) [a, b] = [b, a + b];
    return a;
}
const f50 = fib(50);

console.log(`OK: matmul ${n}x${n} identity check=${ok}, fib(50)=${f50}`);
""",
        "expected_substr": "OK: matmul 50x50",
    },
}

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Result:
    lang: str
    elapsed: float
    status: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    error: str = ""


@dataclass
class LangReport:
    lang: str
    total: int
    success: int
    latencies: list[float] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        return self.success / self.total * 100 if self.total else 0

    @property
    def p50(self) -> float:
        return statistics.median(self.latencies) if self.latencies else 0

    @property
    def p95(self) -> float:
        if not self.latencies:
            return 0
        s = sorted(self.latencies)
        idx = max(0, int(len(s) * 0.95) - 1)
        return s[idx]

    @property
    def mean(self) -> float:
        return statistics.mean(self.latencies) if self.latencies else 0


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

async def execute_once(client: httpx.AsyncClient, payload: dict, expected: str) -> Result:
    lang = payload["lang"]
    t0 = time.perf_counter()
    try:
        resp = await client.post(
            f"{BASE_URL}/api/v1/execute",
            json={
                "code": payload["code"],
                "lang": lang,
                "timeout": TIMEOUT,
                "memory": 256,
            },
            timeout=TIMEOUT + 30,
        )
        elapsed = time.perf_counter() - t0
        if resp.status_code != 200:
            return Result(lang=lang, elapsed=elapsed, status="http_error",
                          error=f"HTTP {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        status = data.get("status", "error")
        stdout = data.get("stdout", "")
        stderr = data.get("stderr", "")
        if status == "success" and expected not in stdout:
            status = "wrong_output"
        return Result(lang=lang, elapsed=elapsed, status=status,
                      stdout=stdout, stderr=stderr,
                      exit_code=data.get("exit_code", 0))
    except (httpx.HTTPError, OSError, asyncio.TimeoutError) as exc:
        return Result(lang=lang, elapsed=time.perf_counter() - t0,
                      status="exception", error=str(exc))


async def run_concurrent(lang: str, payload: dict, concurrency: int) -> LangReport:
    expected = payload["expected_substr"]
    sem = asyncio.Semaphore(concurrency)

    async def bounded(client):
        async with sem:
            return await execute_once(client, payload, expected)

    async with httpx.AsyncClient() as client:
        tasks = [bounded(client) for _ in range(concurrency)]
        results: list[Result] = await asyncio.gather(*tasks)

    report = LangReport(lang=lang, total=len(results), success=0)
    for r in results:
        if r.status == "success":
            report.success += 1
            report.latencies.append(r.elapsed)
        else:
            print(f"  [FAIL] {lang}: status={r.status} stdout={r.stdout[:80]!r} "
                  f"stderr={r.stderr[:120]!r} err={r.error!r}")
    return report


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("lang", list(PAYLOADS.keys()))
async def test_single_execution(lang: str):
    """Each language executes once and produces correct output."""
    payload = PAYLOADS[lang]
    async with httpx.AsyncClient() as client:
        result = await execute_once(client, payload, payload["expected_substr"])

    print(f"\n[{lang}] status={result.status} elapsed={result.elapsed:.2f}s "
          f"stdout={result.stdout[:100]!r}")

    assert result.status == "success", (
        f"{lang}: expected success, got {result.status!r}\n"
        f"  stdout: {result.stdout[:300]}\n"
        f"  stderr: {result.stderr[:300]}"
    )
    assert payload["expected_substr"] in result.stdout


@pytest.mark.asyncio
async def test_stress_all_languages():
    """
    Sends CONCURRENCY concurrent requests per language, then prints a summary table.
    Asserts >= 80% success rate per language and p95 < timeout.
    """
    print(f"\n{'='*65}")
    print(f"  STRESS TEST  |  {CONCURRENCY} concurrent requests per language")
    print(f"  BASE_URL: {BASE_URL}")
    print(f"{'='*65}\n")

    reports: list[LangReport] = []
    for lang, payload in PAYLOADS.items():
        print(f"Running {CONCURRENCY}x {lang} ...", flush=True)
        t_start = time.perf_counter()
        report = await run_concurrent(lang, payload, CONCURRENCY)
        wall = time.perf_counter() - t_start
        print(f"  done in {wall:.1f}s | success={report.success}/{report.total} "
              f"mean={report.mean:.2f}s p95={report.p95:.2f}s")
        reports.append(report)

    # --- Summary table ---
    print(f"\n{'─'*65}")
    print(f"{'Language':<14} {'Total':>6} {'OK':>5} {'Rate':>7} {'Mean':>8} {'P50':>8} {'P95':>8}")
    print(f"{'─'*65}")
    for r in reports:
        print(f"{r.lang:<14} {r.total:>6} {r.success:>5} {r.success_rate:>6.1f}% "
              f"{r.mean:>7.2f}s {r.p50:>7.2f}s {r.p95:>7.2f}s")
    print(f"{'─'*65}\n")

    # --- Assertions ---
    for r in reports:
        assert r.success_rate >= 80, (
            f"{r.lang}: success rate {r.success_rate:.1f}% < 80% "
            f"({r.success}/{r.total} succeeded)"
        )
        if r.latencies:
            assert r.p95 < TIMEOUT, (
                f"{r.lang}: p95 latency {r.p95:.2f}s >= timeout {TIMEOUT}s"
            )
