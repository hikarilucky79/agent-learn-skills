#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${AGENT_LEARN_SKILLS_REPO:-https://github.com/hikarilucky79/agent-learn-skills}"
REF="${AGENT_LEARN_SKILLS_REF:-main}"

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

SRC_DIR=""
if command -v git >/dev/null 2>&1; then
  git clone --depth 1 --branch "$REF" "$REPO_URL.git" "$TMP_DIR/repo" >/dev/null 2>&1
  SRC_DIR="$TMP_DIR/repo"
elif command -v curl >/dev/null 2>&1 && command -v tar >/dev/null 2>&1; then
  curl -fsSL "$REPO_URL/archive/refs/heads/$REF.tar.gz" -o "$TMP_DIR/repo.tar.gz"
  tar -xzf "$TMP_DIR/repo.tar.gz" -C "$TMP_DIR"
  SRC_DIR="$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
else
  echo "ERROR: 'git' or ('curl' + 'tar') is required to download agent-learn-skills." >&2
  exit 1
fi

chmod +x "$SRC_DIR/scripts/install.sh"
exec bash "$SRC_DIR/scripts/install.sh" --copy "$@"
