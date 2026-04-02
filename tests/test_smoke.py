import os

import httpx
import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
EXECUTE_URL = f"{BASE_URL}/api/v1/execute"
RUN_DEPLOYED_SMOKE = os.getenv("RUN_DEPLOYED_SMOKE", "").lower() in {"1", "true", "yes"}

REQUEST_TIMEOUT = 200

EXPECTED = "Hello, World!"
pytestmark = pytest.mark.skipif(
    not RUN_DEPLOYED_SMOKE,
    reason="set RUN_DEPLOYED_SMOKE=1 to run deployed smoke tests",
)

HELLO_WORLD: dict[str, str] = {
    "python": 'print("Hello, World!")',
    "cpp": r"""
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
""",
    "javascript": 'console.log("Hello, World!");',
    "go": r"""
package main
import "fmt"
func main() {
    fmt.Println("Hello, World!")
}
""",
    "java": r"""
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
""",
    "php": '<?php echo "Hello, World!\\n"; ?>',
    "csharp": r"""
using System;
class Program {
    static void Main() {
        Console.WriteLine("Hello, World!");
    }
}
""",
    "bash": 'echo "Hello, World!"',
    "typescript": 'console.log("Hello, World!");',
    "rust": r"""
fn main() {
    println!("Hello, World!");
}
""",
    "lua": 'print("Hello, World!")',
    "r": 'cat("Hello, World!\\n")',
    "perl": 'print "Hello, World!\\n";',
    "d": r"""
import std.stdio;
void main() {
    writeln("Hello, World!");
}
""",
    "ruby": 'puts "Hello, World!"',
    "scala": r"""
object Main {
  def main(args: Array[String]): Unit = {
    println("Hello, World!")
  }
}
""",
    "julia": 'println("Hello, World!")',
    "kotlin": 'println("Hello, World!")',
    "swift": 'print("Hello, World!")',
    "racket": '#lang racket\n(displayln "Hello, World!")',
    "lean": '#eval IO.println "Hello, World!"',
    "verilog": r"""
module tb;
  initial begin
    $display("Hello, World!");
    $finish;
  end
endmodule
""",
}

GPU_BLOCKLIST: set[str] = set()

SKIP_LANGUAGES: set[str] = set(filter(None, (s.strip() for s in os.getenv("SKIP_SMOKE_LANGUAGES", "").split(","))))


def _execute(lang: str, code: str) -> dict:
    payload: dict = {
        "code": code,
        "lang": lang,
        "timeout": 120,
        "memory": 4096,
    }
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        resp = client.post(EXECUTE_URL, json=payload)
        resp.raise_for_status()
        return resp.json()


def test_health():
    with httpx.Client(timeout=10) as client:
        resp = client.get(f"{BASE_URL}/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


def _smoke_languages():
    return sorted(HELLO_WORLD.keys() - GPU_BLOCKLIST - SKIP_LANGUAGES)


@pytest.mark.parametrize("lang", _smoke_languages())
def test_hello_world(lang: str):
    code = HELLO_WORLD[lang]
    result = _execute(lang, code)

    assert result["status"] == "success", (
        f"[{lang}] status={result['status']}, stderr={result.get('stderr', '')!r}, exit_code={result.get('exit_code')}"
    )
    assert EXPECTED in result["stdout"], f"[{lang}] expected '{EXPECTED}' in stdout, got: {result['stdout']!r}"
