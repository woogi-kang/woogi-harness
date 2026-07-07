#!/usr/bin/env bash
# sync-to-projects.sh — claude-craft 하네스를 다른 프로젝트에 동기화
#
# Usage:
#   bash scripts/sync-to-projects.sh                    # 등록된 모든 프로젝트에 동기화
#   bash scripts/sync-to-projects.sh /path/to/project   # 특정 프로젝트에만 동기화
#
# 동기화 대상: 루트 엔트리포인트(CLAUDE/AGENTS/GEMINI), contexts, .agents/skills,
#              .claude 공유 자산(agents, commands, hooks, rules, skills, templates, evals, statusline.py)
# 제외: 프로젝트별 권한/MCP 설정(.claude/settings*.json, .mcp.json), logs/

set -euo pipefail

CRAFT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="${CRAFT_DIR}/.claude"

# 동기화할 루트 디렉토리 목록
ROOT_SYNC_DIRS=(contexts)

# 동기화할 .claude 디렉토리/파일 목록
SYNC_DIRS=(agents commands hooks rules skills templates evals)
SYNC_FILES=(statusline.py)
RSYNC_EXCLUDES=(--exclude='.git' --exclude='logs/' --exclude='__pycache__/' --exclude='*.pyc')

# 등록된 프로젝트 목록 (필요시 추가)
DEFAULT_PROJECTS=(
  "/Users/woogi/Development/memoriz"
  "/Users/woogi/Development/memoriz-invite"
  "/Users/woogi/Documents/Playground"
)

# 인자가 있으면 해당 프로젝트만, 없으면 전체
if [[ $# -gt 0 ]]; then
  PROJECTS=("$@")
else
  PROJECTS=("${DEFAULT_PROJECTS[@]}")
fi

sync_project() {
  local target="$1"
  local target_claude="${target}/.claude"

  if [[ ! -d "$target" ]]; then
    echo "SKIP: $target (디렉토리 없음)"
    return
  fi

  echo "=== Syncing to: $target ==="

  cleanup_generated() {
    local path="$1"
    if [[ -d "$path" ]]; then
      find "$path" -type d -name '__pycache__' -prune -exec rm -rf {} +
      find "$path" -type f -name '*.pyc' -delete
    fi
  }

  # 멀티 환경 엔트리포인트 동기화
  cp "${CRAFT_DIR}/CLAUDE.md" "${target}/CLAUDE.md"
  rm -f "${target}/AGENTS.md" "${target}/GEMINI.md"
  ln -s "CLAUDE.md" "${target}/AGENTS.md"
  ln -s "CLAUDE.md" "${target}/GEMINI.md"
  echo "  SYNC: CLAUDE.md + AGENTS.md/GEMINI.md symlinks ✓"

  mkdir -p "${target}/.agents"
  rm -rf "${target}/.agents/skills"
  ln -s "../.claude/skills" "${target}/.agents/skills"
  echo "  SYNC: .agents/skills symlink ✓"

  for dir in "${ROOT_SYNC_DIRS[@]}"; do
    local src="${CRAFT_DIR}/${dir}"
    local dst="${target}/${dir}"

    if [[ ! -e "$src" ]]; then
      echo "  SKIP: ${dir} (소스 없음)"
      continue
    fi

    if [[ -L "$dst" ]]; then
      echo "  REMOVE symlink: ${dir}"
      rm "$dst"
    fi

    cleanup_generated "$dst"
    rsync -a --delete "${RSYNC_EXCLUDES[@]}" "${src}/" "${dst}/"
    echo "  SYNC: ${dir} ✓"
  done

  # .claude 디렉토리 확보
  mkdir -p "$target_claude"

  for dir in "${SYNC_DIRS[@]}"; do
    local src="${SOURCE}/${dir}"
    local dst="${target_claude}/${dir}"

    if [[ ! -e "$src" ]]; then
      echo "  SKIP: ${dir} (소스 없음)"
      continue
    fi

    # 기존 symlink면 제거
    if [[ -L "$dst" ]]; then
      echo "  REMOVE symlink: ${dir}"
      rm "$dst"
    fi

    # rsync로 동기화 (삭제된 파일도 반영, .git 제외)
    cleanup_generated "$dst"
    rsync -a --delete "${RSYNC_EXCLUDES[@]}" "${src}/" "${dst}/"
    echo "  SYNC: ${dir} ✓"
  done

  for file in "${SYNC_FILES[@]}"; do
    local src="${SOURCE}/${file}"
    local dst="${target_claude}/${file}"

    if [[ ! -e "$src" ]]; then
      echo "  SKIP: ${file} (소스 없음)"
      continue
    fi

    cp "$src" "$dst"
    echo "  SYNC: ${file} ✓"
  done

  echo ""
}

echo "Source: ${SOURCE}"
echo ""

for project in "${PROJECTS[@]}"; do
  sync_project "$project"
done

echo "Done."
