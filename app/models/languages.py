from __future__ import annotations

from typing import Final

LANGUAGE_IDS: Final[tuple[str, ...]] = (
    "bash",
    "cpp",
    "csharp",
    "cuda",
    "d",
    "go",
    "java",
    "javascript",
    "js",
    "julia",
    "kotlin",
    "lean",
    "lua",
    "perl",
    "php",
    "python",
    "r",
    "ruby",
    "rust",
    "scala",
    "sql",
    "swift",
    "racket",
    "ts",
    "typescript",
    "verilog",
)

_LANG_MAP: Final[dict[str, str]] = {
    "javascript": "nodejs",
    "r": "R",
    "kotlin": "kotlin_script",
    "d": "D_ut",
}


def resolve_lang(lang: str) -> str:
    return _LANG_MAP.get(lang, lang)


def lang_metadata() -> list[dict[str, str]]:
    return [_META[lid] for lid in LANGUAGE_IDS]


_PYTHON_PACKAGES: Final[str] = (
    "absl-py, antlr4-python3-runtime, APScheduler, arch, astor, beautifulsoup4, catboost, colorama, "
    "coverage, cryptography, cvxpy, datasketch, Django, docker, faiss-cpu, Faker, fastdtw, Flask, "
    "folium, gensim, GitPython, gmpy2, graphene, grpcio-tools, jsonlines, jupyter, kaleido, kneed, "
    "lightgbm, lxml, matplotlib, mongomock, nameko, nltk, numba, numpy, opencv-python, openpyxl, "
    "pandas, pandasql, pika, pillow, plotly, pmdarima, psutil, pulp, pyberny, pycryptodome, "
    "pydantic, PyJWT, pymongo, PyMuPDF, PyQt5, pyscf, pytest, python-docx, pyzbar, rdkit, redis, "
    "requests, ruptures, scikit-image, scikit-learn, scipy, seaborn, shapely, statsmodels, tabulate, "
    "tensorflow, textblob, toml, torch, tree-sitter, uvloop, xarray, xgboost, yolk"
)

_META: Final[dict[str, dict[str, str]]] = {
    "python": {
        "id": "python",
        "title": "Python",
        "description": (
            "Ubuntu 20.04, conda-managed Python 3.11.15. Main pip packages (alphabetically; "
            "satellites in the same stack folded into one name, e.g. Flask-RESTful→Flask, "
            "requests-toolbelt→requests): "
            f"{_PYTHON_PACKAGES}."
        ),
    },
    "cpp": {
        "id": "cpp",
        "title": "C++",
        "description": (
            "Ubuntu 20.04, g++ 9.4.0, Boost (libboost in the image); compile and run a binary in a temporary directory."
        ),
    },
    "javascript": {
        "id": "javascript",
        "title": "JavaScript",
        "description": (
            "Node.js 20.11.0; global npm TypeScript 5.3.3 and tsx 4.7.1; execution symlinks the image "
            "node_modules layer (jest, puppeteer, @babel/*, lodash, jsdom, etc. per the image package.json)."
        ),
    },
    "js": {
        "id": "js",
        "title": "JavaScript (js)",
        "description": "Same stack as javascript: Node.js 20.11.0 and the bundled Node dependency tree.",
    },
    "go": {
        "id": "go",
        "title": "Go",
        "description": "Go 1.23.3 (linux/amd64); GOPROXY as set when the image was built.",
    },
    "java": {
        "id": "java",
        "title": "Java",
        "description": "JDK 21.0.7 LTS; compile and run an entrypoint main.",
    },
    "php": {
        "id": "php",
        "title": "PHP",
        "description": "PHP 7.4.3 CLI from Ubuntu 20.04.",
    },
    "csharp": {
        "id": "csharp",
        "title": "C#",
        "description": ".NET SDK 8.0.410; build and dotnet run.",
    },
    "bash": {
        "id": "bash",
        "title": "Bash",
        "description": "GNU Bash from Ubuntu 20.04; script in a temporary .sh file.",
    },
    "typescript": {
        "id": "typescript",
        "title": "TypeScript",
        "description": "Runs via global tsx 4.7.1 on Node 20.11.0; same symlinked node_modules layer as JavaScript.",
    },
    "ts": {
        "id": "ts",
        "title": "TypeScript (ts)",
        "description": "Same stack as typescript: tsx, Node 20.11.0, bundled Node dependencies.",
    },
    "sql": {
        "id": "sql",
        "title": "SQL",
        "description": "Catalog id only; this deployment has no SQL execution handler, so runs are unavailable.",
    },
    "rust": {
        "id": "rust",
        "title": "Rust",
        "description": "Rust 1.76.0 via rustup; rustc and link in a temporary directory.",
    },
    "cuda": {
        "id": "cuda",
        "title": "CUDA",
        "description": (
            "Build expects cmake, make, and build/main; the checked server image has no nvcc and no cmake—extend "
            "the image or host before CUDA projects can build."
        ),
    },
    "lua": {
        "id": "lua",
        "title": "Lua",
        "description": "Lua 5.2.4; LuaRocks in image: luaunit 3.4-1.",
    },
    "perl": {
        "id": "perl",
        "title": "Perl",
        "description": "Perl from Ubuntu 20.04; image includes CPAN modules Test::Deep and Data::Compare.",
    },
    "ruby": {
        "id": "ruby",
        "title": "Ruby",
        "description": "Ruby 2.7.0 from Ubuntu 20.04 packages.",
    },
    "scala": {
        "id": "scala",
        "title": "Scala",
        "description": "Scala 2.11.12; scalac and scala for an object with main.",
    },
    "julia": {
        "id": "julia",
        "title": "Julia",
        "description": "Julia 1.4.1 from distro packages in the image.",
    },
    "kotlin": {
        "id": "kotlin",
        "title": "Kotlin",
        "description": "Kotlin 2.0.0 (kotlinc JVM); .kts scripts via kotlin CLI.",
    },
    "swift": {
        "id": "swift",
        "title": "Swift",
        "description": "Swift 5.10.1 on Ubuntu 20.04; swiftc and run the binary.",
    },
    "racket": {
        "id": "racket",
        "title": "Racket",
        "description": "Racket 7.2 from distro packages in the image.",
    },
    "lean": {
        "id": "lean",
        "title": "Lean",
        "description": "Lean 4.10.0-rc2; lake build with the bundled lean template (packages, lakefile, toolchain).",
    },
    "verilog": {
        "id": "verilog",
        "title": "Verilog",
        "description": "Icarus Verilog 13.0 (devel), top module tb; iverilog compile then vvp.",
    },
    "d": {
        "id": "d",
        "title": "D",
        "description": "DMD 2.111.0; build with -unittest as in the image.",
    },
    "r": {
        "id": "r",
        "title": "R",
        "description": "R 3.6.3; run via Rscript on a temporary .R file.",
    },
}
