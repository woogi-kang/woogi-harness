#!/bin/bash
#
# smart-ai.sh - Multi-LLM Router for Solo Unicorn
#
# Routes tasks to optimal AI model based on task type:
# - Gemini CLI: OCR, image analysis (FREE 1,000/day)
# - Claude: Reasoning, long documents, contracts
# - Codex: Code generation, refactoring
#
# Usage:
#   ./smart-ai.sh ocr receipt.jpg
#   ./smart-ai.sh contract agreement.pdf "위험 조항 분석"
#   ./smart-ai.sh code app.py "버그 수정"
#   ./smart-ai.sh review src/
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if required tools are installed
check_dependencies() {
  local missing=()

  if ! command -v gemini &> /dev/null; then
    missing+=("gemini-cli (npm i -g @google/gemini-cli)")
  fi

  if ! command -v claude &> /dev/null; then
    missing+=("claude-code (curl -fsSL https://claude.ai/install.sh | bash)")
  fi

  if [ ${#missing[@]} -gt 0 ]; then
    log_warn "Optional tools not found:"
    for tool in "${missing[@]}"; do
      echo "  - $tool"
    done
  fi
}

# OCR with Gemini CLI (FREE)
do_ocr() {
  local file="$1"
  local prompt="${2:-이 영수증에서 다음 정보를 JSON으로 추출해줘: vendor, date, items, total, vat, category}"

  if [ ! -f "$file" ]; then
    log_error "File not found: $file"
    exit 1
  fi

  log_info "Processing OCR with Gemini CLI (FREE tier)..."
  gemini "$prompt" --image "$file"
}

# Batch OCR processing
do_ocr_batch() {
  local dir="$1"
  local output_dir="${2:-$dir/processed}"

  if [ ! -d "$dir" ]; then
    log_error "Directory not found: $dir"
    exit 1
  fi

  mkdir -p "$output_dir"

  local count=0
  local failed=0

  # Process each image type separately for better compatibility
  for ext in jpg jpeg png pdf; do
    for img in "$dir"/*."$ext"; do
      [ -f "$img" ] || continue

      local filename=$(basename "$img")
      local output_file="$output_dir/${filename%.*}.json"

      # Skip if already processed
      if [ -f "$output_file" ]; then
        log_info "Skipping (already processed): $filename"
        continue
      fi

      log_info "Processing: $filename"

      # OCR with error handling and validation
      if ! gemini "영수증 JSON 추출: vendor, date, items, total, vat, category" --image "$img" > "$output_file" 2>/dev/null; then
        log_error "OCR failed for $filename"
        rm -f "$output_file"
        ((failed++))
        continue
      fi

      # Validate JSON output
      if ! jq empty "$output_file" 2>/dev/null; then
        log_warn "Invalid JSON output for $filename, retrying..."
        rm -f "$output_file"
        ((failed++))
        continue
      fi

      ((count++))

      # Rate limit: 1 second between requests
      sleep 1
    done
  done

  if [ "$failed" -gt 0 ]; then
    log_warn "Failed to process $failed files"
  fi

  log_success "Processed $count files"
}

# Contract/Legal analysis with Claude
do_contract() {
  local file="$1"
  local prompt="${2:-이 계약서를 분석하고 위험 조항을 식별해줘}"

  if [ ! -f "$file" ]; then
    log_error "File not found: $file"
    exit 1
  fi

  log_info "Analyzing with Claude (high accuracy for legal docs)..."
  claude "$prompt" --file "$file"
}

# Code generation/refactoring with Codex
do_code() {
  local file="$1"
  local prompt="${2:-이 코드를 리뷰하고 개선점을 제안해줘}"

  if [ ! -f "$file" ]; then
    log_error "File not found: $file"
    exit 1
  fi

  log_info "Processing with Claude Code..."
  claude "$prompt" --file "$file"
}

# Multi-LLM code review (consensus from multiple models)
do_review() {
  local target="$1"
  local temp_dir=$(mktemp -d)

  log_info "Running multi-LLM code review..."

  # Claude review
  log_info "Getting Claude's review..."
  claude "코드 리뷰: 버그, 보안 취약점, 개선점을 찾아줘" --file "$target" > "$temp_dir/claude_review.md" 2>/dev/null || true

  # If Gemini available, get its review too
  if command -v gemini &> /dev/null; then
    log_info "Getting Gemini's review..."
    gemini "코드 리뷰: 버그, 보안 취약점, 개선점" --file "$target" > "$temp_dir/gemini_review.md" 2>/dev/null || true
  fi

  # Synthesize reviews with Claude
  log_info "Synthesizing reviews..."
  if [ -f "$temp_dir/gemini_review.md" ]; then
    claude "다음 두 리뷰를 종합해서 합의된 피드백을 생성해줘:

--- Claude Review ---
$(cat $temp_dir/claude_review.md)

--- Gemini Review ---
$(cat $temp_dir/gemini_review.md)
"
  else
    cat "$temp_dir/claude_review.md"
  fi

  # Cleanup
  rm -rf "$temp_dir"
}

# Expense classification with the provider's configured fast-scan quality tier
do_classify() {
  local file="$1"

  log_info "Classifying expense with Claude..."
  claude "다음 영수증 데이터를 분류해줘.
카테고리: 인건비, 서버/인프라, 마케팅, 소프트웨어/구독, 사무실/운영, 복리후생, 여비교통, 기타

데이터:
$(cat $file)

JSON 응답: {category, confidence, reasoning}"
}

# Financial report generation
do_finance_report() {
  local month="${1:-$(date -v-1m +%Y-%m 2>/dev/null || date -d 'last month' +%Y-%m)}"

  log_info "Generating financial report for $month..."

  # Check if ledger exists
  local ledger="operations/finance/ledger.json"
  if [ ! -f "$ledger" ]; then
    log_error "Ledger not found: $ledger"
    log_info "Create the ledger first or specify a different path"
    exit 1
  fi

  claude "다음 원장 데이터로 $month 월간 재무 리포트를 생성해줘.
포함할 내용:
1. 손익계산서 (P&L)
2. 주요 지표 (매출, 비용, 순이익, 마진율)
3. 카테고리별 비용 breakdown
4. 전월 대비 변화
5. 주의가 필요한 항목

원장 데이터:
$(cat $ledger | head -200)"
}

# Help message
show_help() {
  cat << EOF
smart-ai.sh - Multi-LLM Router for Solo Unicorn

Usage: ./smart-ai.sh <command> [args]

Commands:
  ocr <image>              OCR single receipt with Gemini (FREE)
  ocr-batch <dir>          Batch OCR all receipts in directory
  contract <file> [prompt] Analyze contract with Claude
  code <file> [prompt]     Code review/refactor with Claude
  review <file|dir>        Multi-LLM consensus code review
  classify <json>          Classify expense from OCR result
  finance [YYYY-MM]        Generate monthly financial report

Examples:
  ./smart-ai.sh ocr receipt.jpg
  ./smart-ai.sh ocr-batch ./receipts
  ./smart-ai.sh contract agreement.pdf "위험 조항 분석"
  ./smart-ai.sh review src/auth.ts
  ./smart-ai.sh finance 2026-01

Cost Comparison (monthly, 1000 tasks):
  - External OCR: \$50-500
  - Multi-LLM:    ~\$5 (Gemini FREE + Claude classify)
  - Savings:      90-99%

EOF
}

# Main router
main() {
  local command="$1"
  shift || true

  check_dependencies

  case "$command" in
    ocr)
      do_ocr "$@"
      ;;
    ocr-batch)
      do_ocr_batch "$@"
      ;;
    contract|legal|analyze)
      do_contract "$@"
      ;;
    code|generate|refactor)
      do_code "$@"
      ;;
    review)
      do_review "$@"
      ;;
    classify)
      do_classify "$@"
      ;;
    finance|financial-report)
      do_finance_report "$@"
      ;;
    help|--help|-h)
      show_help
      ;;
    *)
      log_error "Unknown command: $command"
      show_help
      exit 1
      ;;
  esac
}

main "$@"
