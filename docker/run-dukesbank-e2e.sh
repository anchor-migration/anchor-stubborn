#!/usr/bin/env bash
# Duke's Bank bank module -> scip-java -> anchor-stubborn (AccountControllerBean)
set -euo pipefail

BANK_ROOT="${BANK_ROOT:-/bank}"
EXAMPLE_ROOT="${EXAMPLE_ROOT:-/opt/anchor-stubborn/examples/dukesbank}"
METADATA_DIR="${EXAMPLE_ROOT}/metadata"

if [[ ! -d "${BANK_ROOT}/src" ]]; then
    echo "Missing Duke's Bank module at ${BANK_ROOT}" >&2
    echo "Mount dukesbank/.../examples/bank to /bank or set BANK_ROOT." >&2
    exit 1
fi

cd "${BANK_ROOT}"

echo "== Duke's Bank anchor-stubborn E2E (Docker) =="
echo "Bank module: ${BANK_ROOT}"

echo
echo "[1/6] Maven compile..."
mvn -q -DskipTests package

echo
echo "[2/6] scip-java index..."
rm -f index.scip
scip-java index
test -f index.scip

mkdir -p "${METADATA_DIR}"
rm -f "${METADATA_DIR}/symbols.db"

echo
echo "[3/6] anchor-stubborn index..."
anchor-stubborn index --scip index.scip --out "${METADATA_DIR}/symbols.db"

echo
echo "[4/6] resolve AccountControllerBean..."
target="$(python3 /opt/anchor-stubborn/scripts/resolve_symbol.py \
    "${METADATA_DIR}/symbols.db" --display-name AccountControllerBean)"
echo "Target: ${target}"

echo
echo "[5/6] emit java-stub + anchor-dsl..."
anchor-stubborn context "${METADATA_DIR}/symbols.db" \
    --target "${target}" \
    --out "${METADATA_DIR}/account-controller.stub.java"
anchor-stubborn context "${METADATA_DIR}/symbols.db" \
    --target "${target}" \
    --format anchor-dsl \
    --member-signatures neighbors \
    --javadoc summary \
    --out "${METADATA_DIR}/account-controller.anchor-dsl"

echo
echo "[6/6] metrics..."
anchor-stubborn metrics "${METADATA_DIR}/symbols.db" \
    --target "${target}" \
    --sources src

echo
echo "Done."
echo "  SQLite graph: ${METADATA_DIR}/symbols.db"
echo "  java-stub   : ${METADATA_DIR}/account-controller.stub.java"
echo "  anchor-dsl  : ${METADATA_DIR}/account-controller.anchor-dsl"
