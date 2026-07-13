# Woogi Harness Makefile

.PHONY: install install-copy export uninstall status help clean publish

.DEFAULT_GOAL := help

SCRIPT := ./scripts/install.sh
CLAUDE_HOME := $(HOME)/.claude

install:
	@echo "Installing Woogi Harness..."
	@$(SCRIPT) --link

install-copy:
	@echo "Installing Woogi Harness..."
	@$(SCRIPT) --copy

export:
	@echo "Creating distribution package..."
	@$(SCRIPT) --export

uninstall:
	@echo "Uninstalling Woogi Harness components..."
	@rm -f "$(CLAUDE_HOME)/statusline.py"
	@rm -rf "$(CLAUDE_HOME)/agents" "$(CLAUDE_HOME)/skills" "$(CLAUDE_HOME)/hooks" "$(CLAUDE_HOME)/commands"
	@echo "Done. settings.json preserved."

status:
	@echo "Woogi Harness Installation Status"
	@echo "================================"
	@if [ -f "$(CLAUDE_HOME)/statusline.py" ]; then echo "statusline.py: installed"; else echo "statusline.py: not installed"; fi
	@if [ -d "$(CLAUDE_HOME)/agents" ]; then echo "agents/: installed"; else echo "agents/: not installed"; fi
	@if [ -d "$(CLAUDE_HOME)/skills" ]; then echo "skills/: installed"; else echo "skills/: not installed"; fi
	@if [ -d "$(CLAUDE_HOME)/hooks" ]; then echo "hooks/: installed"; else echo "hooks/: not installed"; fi
	@if [ -d "$(CLAUDE_HOME)/commands" ]; then echo "commands/: installed"; else echo "commands/: not installed"; fi

help:
	@echo "Woogi Harness Commands"
	@echo "====================="
	@echo "install       심볼릭 링크로 설치"
	@echo "install-copy  파일 복사로 설치"
	@echo "export        배포 패키지(.zip) 생성"
	@echo "uninstall     설치 컴포넌트 제거"
	@echo "status        현재 설치 상태 확인"
	@echo "clean         dist 폴더 정리"
	@echo "publish       원격 설치 스크립트 배포 준비"

clean:
	@rm -rf ./dist
	@echo "Cleaned."

publish:
	@chmod +x ./docs/install.sh
	@echo "Remote installer is ready."
