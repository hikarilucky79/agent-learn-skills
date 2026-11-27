#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"

AGENT="claude"
SCOPE="global"
MODE="symlink"
MODE_EXPLICIT=false
UNINSTALL=false
TARGET_DIR=""
FORCE=false
SELECTED_SKILLS=()
SKILL_NAME_RE='^[a-z0-9]+(-[a-z0-9]+)*$'

usage() {
  cat <<'EOF'
Uso: ./scripts/install.sh [opções]

Opções:
  -a, --agent <nome>     Agente destino: claude | cursor | codex | opencode | antigravity (padrão: claude)
  -s, --scope <escopo>   Escopo: global | project (padrão: global)
  -t, --target <dir>     Diretório destino customizado (sobrescreve --agent e --scope)
  -k, --skill <nome>     Seleciona apenas a skill informada (pode repetir a flag)
  -c, --copy             Copia as pastas em vez de criar symlinks
  -u, --uninstall        Remove do destino as skills selecionadas deste repositório
  -f, --force            Sobrescreve skills existentes (instalação) ou remove symlinks externos (desinstalação)
  -h, --help             Exibe esta ajuda
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -a|--agent) AGENT="${2:?Falta valor para --agent}"; shift 2 ;;
    -s|--scope) SCOPE="${2:?Falta valor para --scope}"; shift 2 ;;
    -t|--target) TARGET_DIR="${2:?Falta valor para --target}"; shift 2 ;;
    -k|--skill) SELECTED_SKILLS+=("${2:?Falta valor para --skill}"); shift 2 ;;
    -c|--copy) MODE="copy"; MODE_EXPLICIT=true; shift ;;
    -u|--uninstall) UNINSTALL=true; shift ;;
    -f|--force) FORCE=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Opção desconhecida: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ "$UNINSTALL" == true && "$MODE_EXPLICIT" == true ]]; then
  echo "ERRO: --uninstall não pode ser combinado com --copy." >&2
  exit 1
fi

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

resolve_path_safe() {
  local raw="$1"
  local trimmed="${raw%/}"
  if [[ -z "$trimmed" ]]; then
    trimmed="/"
  fi
  local resolved=""
  if [[ -d "$trimmed" ]]; then
    if resolved="$(cd "$trimmed" 2>/dev/null && pwd -P)"; then
      echo "$resolved"
      return 0
    fi
  fi
  local dir base
  dir="$(dirname "$trimmed")"
  base="$(basename "$trimmed")"
  if [[ -d "$dir" ]]; then
    if resolved="$(cd "$dir" 2>/dev/null && pwd -P)"; then
      echo "$resolved/$base"
      return 0
    fi
  fi
  echo "$trimmed"
}

DEST_DIR="$(resolve_target)"
if [[ "$DEST_DIR" != "/" ]]; then
  DEST_DIR="${DEST_DIR%/}"
fi

if [[ ${#SELECTED_SKILLS[@]} -eq 0 ]]; then
  for dir in "$SKILLS_SRC"/*/; do
    [[ -d "$dir" ]] || continue
    SELECTED_SKILLS+=("$(basename "$dir")")
  done
fi

for skill in "${SELECTED_SKILLS[@]}"; do
  if [[ ! "$skill" =~ $SKILL_NAME_RE ]]; then
    echo "ERRO: nome de skill inválido: '$skill'" >&2
    exit 1
  fi
  if [[ ! -f "$SKILLS_SRC/$skill/SKILL.md" ]]; then
    echo "ERRO: skill '$skill' não encontrada em $SKILLS_SRC/$skill" >&2
    exit 1
  fi
done

if [[ "$UNINSTALL" == true ]]; then
  if [[ ! -e "$DEST_DIR" && ! -L "$DEST_DIR" ]]; then
    echo "Diretório destino não existe: $DEST_DIR"
    echo "Concluído: 0 removida(s), ${#SELECTED_SKILLS[@]} pulada(s) em $DEST_DIR"
    exit 0
  fi

  if [[ ! -d "$DEST_DIR" ]]; then
    echo "ERRO: destino não é um diretório: $DEST_DIR" >&2
    exit 1
  fi

  removed=0
  skipped=0

  for skill in "${SELECTED_SKILLS[@]}"; do
    src="$SKILLS_SRC/$skill"
    dst="$DEST_DIR/$skill"

    if [[ ! -e "$dst" && ! -L "$dst" ]]; then
      echo "NÃO ENCONTRADA: $skill (ausente em $dst)"
      ((skipped+=1))
      continue
    fi

    if [[ -L "$dst" ]]; then
      link_target="$(readlink "$dst")"
      if [[ "$link_target" != /* ]]; then
        link_target="$(dirname "$dst")/$link_target"
      fi
      resolved_target="$(resolve_path_safe "$link_target")"
      resolved_src="$(resolve_path_safe "$src")"

      if [[ "$resolved_target" == "$resolved_src" ]]; then
        rm -rf "$dst"
        echo "REMOVIDA (symlink): $skill <- $dst"
        ((removed+=1))
      elif [[ "$FORCE" == true ]]; then
        rm -rf "$dst"
        echo "REMOVIDA (symlink externo): $skill <- $dst"
        ((removed+=1))
      else
        echo "PULADA: $skill (symlink aponta para outro destino: $link_target; use --force para remover)"
        ((skipped+=1))
      fi
    else
      rm -rf "$dst"
      echo "REMOVIDA (copy): $skill <- $dst"
      ((removed+=1))
    fi
  done

  echo "Concluído: $removed removida(s), $skipped pulada(s) em $DEST_DIR"
  exit 0
fi

mkdir -p "$DEST_DIR"

installed=0
skipped=0

for skill in "${SELECTED_SKILLS[@]}"; do
  src="$SKILLS_SRC/$skill"
  dst="$DEST_DIR/$skill"

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
