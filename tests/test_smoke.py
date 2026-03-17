import base64
import os

import httpx
import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
EXECUTE_URL = f"{BASE_URL}/api/v1/execute"
RUN_DEPLOYED_SMOKE = os.getenv("RUN_DEPLOYED_SMOKE", "").lower() in {"1", "true", "yes"}

# Таймаут на один запрос (секунды).  Компилируемые языки могут быть медленнее.
REQUEST_TIMEOUT = 120

# Ожидаемая подстрока в stdout для каждого кейса.
EXPECTED = "Hello, World!"
pytestmark = pytest.mark.skipif(
    not RUN_DEPLOYED_SMOKE,
    reason="set RUN_DEPLOYED_SMOKE=1 to run deployed smoke tests",
)

# ---------- Hello-World код для каждого языка ----------

HELLO_WORLD: dict[str, str] = {
    "python": 'print("Hello, World!")',
    "cpp": r"""
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
""",
    "nodejs": 'console.log("Hello, World!");',
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
    "R": 'cat("Hello, World!\\n")',
    "perl": 'print "Hello, World!\\n";',
    "D_ut": r"""
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
    "kotlin_script": 'println("Hello, World!")',
    "swift": 'print("Hello, World!")',
    "racket": '#lang racket\n(displayln "Hello, World!")',
    "lean": '#eval IO.println "Hello, World!"',
    "verilog": r"""
module hello;
  initial begin
    $display("Hello, World!");
    $finish;
  end
endmodule
""",
    # Тест-раннеры
    "pytest": r"""
def test_hello():
    print("Hello, World!")
    assert True
""",
    "junit": r"""
import org.junit.Test;
import static org.junit.Assert.*;
public class MainTest {
    @Test
    public void testHello() {
        System.out.println("Hello, World!");
        assertTrue(true);
    }
}
""",
    "jest": """
test('hello', () => {
  console.log("Hello, World!");
  expect(true).toBe(true);
});
""",
}

# Языки, требующие GPU — пропускаем в стандартном smoke-тесте.
GPU_LANGUAGES = {"cuda", "python_gpu"}


def _execute(lang: str, code: str) -> dict:
    """Отправляет код на исполнение и возвращает JSON-ответ."""
    payload: dict = {
        "code": code,
        "lang": lang,
        "timeout": 120,
        "memory": 4096,
    }
    if lang == "pytest":
        payload["files"] = {
            "pytest.ini": base64.b64encode(b"[pytest]\naddopts = -s\n").decode(),
        }
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        resp = client.post(EXECUTE_URL, json=payload)
        resp.raise_for_status()
        return resp.json()  # type: ignore


# -------------------- Тесты --------------------


def test_health():
    """Проверяем что приложение живо."""
    with httpx.Client(timeout=10) as client:
        resp = client.get(f"{BASE_URL}/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


def _smoke_languages():
    """Языки для smoke-теста: исключаем только GPU."""
    return sorted(HELLO_WORLD.keys() - GPU_LANGUAGES)


@pytest.mark.parametrize("lang", _smoke_languages())
def test_hello_world(lang: str):
    """Запускает Hello World для данного языка и проверяет stdout."""
    code = HELLO_WORLD[lang]
    result = _execute(lang, code)

    assert result["status"] == "success", (
        f"[{lang}] status={result['status']}, stderr={result.get('stderr', '')!r}, exit_code={result.get('exit_code')}"
    )
    assert EXPECTED in result["stdout"], f"[{lang}] expected '{EXPECTED}' in stdout, got: {result['stdout']!r}"


@pytest.mark.parametrize("lang", sorted(GPU_LANGUAGES))
def test_gpu_language_skipped(lang: str):
    """GPU-языки пропускаем — просто помечаем skip."""
    pytest.skip(f"{lang} requires GPU runtime")
