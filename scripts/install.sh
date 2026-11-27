#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"

AGENT="claude"
SCOPE="global"
MODE="symlink"
TARGET_DIR=""
FORCE=false
SELECTED_SKILLS=()

usage() {
  cat <<'EOF'
Uso: ./scripts/install.sh [opções]

Opções:
  -a, --agent <nome>     Agente destino: claude | cursor | codex | opencode | antigravity (padrão: claude)
  -s, --scope <escopo>   Escopo: global | project (padrão: global)
  -t, --target <dir>     Diretório destino customizado (sobrescreve --agent e --scope)
  -k, --skill <nome>     Instala apenas a skill informada (pode repetir a flag)
  -c, --copy             Copia as pastas em vez de criar symlinks
  -f, --force            Sobrescreve skills já existentes no destino
  -h, --help             Exibe esta ajuda
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -a|--agent) AGENT="${2:?Falta valor para --agent}"; shift 2 ;;
    -s|--scope) SCOPE="${2:?Falta valor para --scope}"; shift 2 ;;
    -t|--target) TARGET_DIR="${2:?Falta valor para --target}"; shift 2 ;;
    -k|--skill) SELECTED_SKILLS+=("${2:?Falta valor para --skill}"); shift 2 ;;
    -c|--copy) MODE="copy"; shift ;;
    -f|--force) FORCE=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Opção desconhecida: $1" >&2; usage; exit 1 ;;
  esac
done

resolve_target() {
  if [[ -n "$TARGET_DIR" ]]; then
    echo "$TARGET_DIR"
    return
  fi

  local base
  if [[ "$SCOPE" == "global" ]]; then
    base="$HOME"
  elif [[ "$SCOPE" == "project" ]]; then
    base="$(pwd)"
  else
    echo "Escopo inválido: '$SCOPE' (use global ou project)." >&2
    exit 1
  fi

  case "$AGENT" in
    claude) echo "$base/.claude/skills" ;;
    cursor) echo "$base/.cursor/skills" ;;
    codex|opencode) echo "$base/.agents/skills" ;;
    antigravity)
      if [[ "$SCOPE" == "global" ]]; then
        echo "$HOME/.gemini/antigravity/skills"
      else
        echo "$base/.agent/skills"
      fi
      ;;
    *)
      echo "Agente desconhecido: '$AGENT'." >&2
      exit 1
      ;;
  esac
}

DEST_DIR="$(resolve_target)"
mkdir -p "$DEST_DIR"

if [[ ${#SELECTED_SKILLS[@]} -eq 0 ]]; then
  for dir in "$SKILLS_SRC"/*/; do
    SELECTED_SKILLS+=("$(basename "$dir")")
  done
fi

installed=0
skipped=0

for skill in "${SELECTED_SKILLS[@]}"; do
  src="$SKILLS_SRC/$skill"
  dst="$DEST_DIR/$skill"

  if [[ ! -f "$src/SKILL.md" ]]; then
    echo "ERRO: skill '$skill' não encontrada em $src" >&2
    exit 1
  fi

  if [[ -e "$dst" || -L "$dst" ]]; then
    if [[ "$FORCE" == true ]]; then
      rm -rf "$dst"
    else
      echo "PULADA: $skill (já existe em $dst; use --force para substituir)"
      ((skipped+=1))
      continue
    fi
  fi

  if [[ "$MODE" == "copy" ]]; then
    cp -R "$src" "$dst"
  else
    ln -s "$src" "$dst"
  fi

  echo "INSTALADA ($MODE): $skill -> $dst"
  ((installed+=1))
done

echo "Concluído: $installed instalada(s), $skipped pulada(s) em $DEST_DIR"
