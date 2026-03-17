#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

FAILED=0

echo "=============================="
echo "  Running local CI checks"
echo "=============================="

echo ""
echo ">>> ruff check"
if ruff check app/ tests/; then
    echo -e "${GREEN}ruff: OK${NC}"
else
    echo -e "${RED}ruff: FAILED${NC}"
    FAILED=1
fi

echo ""
echo ">>> ruff format --check"
if ruff format --check app/ tests/; then
    echo -e "${GREEN}ruff format: OK${NC}"
else
    echo -e "${RED}ruff format: FAILED${NC}"
    FAILED=1
fi

echo ""
echo ">>> pylint"
if pylint app/ tests/; then
    echo -e "${GREEN}pylint: OK${NC}"
else
    echo -e "${RED}pylint: FAILED${NC}"
    FAILED=1
fi

echo ""
echo ">>> mypy"
if mypy app/ tests/; then
    echo -e "${GREEN}mypy: OK${NC}"
else
    echo -e "${RED}mypy: FAILED${NC}"
    FAILED=1
fi

echo ""
echo "=============================="
if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
else
    echo -e "${RED}Some checks failed!${NC}"
    exit 1
fi
