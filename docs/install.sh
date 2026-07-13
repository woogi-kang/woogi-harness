#!/bin/bash

set -e

REPO_URL="https://github.com/woogi-kang/woogi-harness.git"
if [ -z "${INSTALL_DIR:-}" ]; then
    if [ -d "$HOME/.woogi-harness/.git" ]; then
        INSTALL_DIR="$HOME/.woogi-harness"
    elif [ -d "$HOME/.claude-craft/.git" ]; then
        # Preserve existing installations created before the public rename.
        INSTALL_DIR="$HOME/.claude-craft"
    else
        INSTALL_DIR="$HOME/.woogi-harness"
    fi
fi
INSTALL_MODE="${INSTALL_MODE:-link}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${BOLD}Woogi Harness Remote Installer${NC}                         ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}     Domain agents, skills, commands, status line         ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

if ! command -v git >/dev/null 2>&1; then
    echo -e "${RED}Error:${NC} git is required"
    exit 1
fi

if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${CYAN}Updating existing installation...${NC}"
    cd "$INSTALL_DIR"
    git fetch origin
    CURRENT_BRANCH="$(git branch --show-current)"
    if [ -n "$CURRENT_BRANCH" ]; then
        git pull --ff-only origin "$CURRENT_BRANCH"
    else
        git pull --ff-only origin main 2>/dev/null || git pull --ff-only origin master
    fi
elif [ -e "$INSTALL_DIR" ] && [ -n "$(ls -A "$INSTALL_DIR" 2>/dev/null)" ]; then
    echo -e "${RED}Error:${NC} $INSTALL_DIR already exists and is not an empty git checkout"
    exit 1
else
    echo -e "${CYAN}Cloning repository to $INSTALL_DIR...${NC}"
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

case "$INSTALL_MODE" in
    link)
        MODE_ARG="--link"
        ;;
    copy)
        MODE_ARG="--copy"
        ;;
    *)
        echo -e "${YELLOW}Unknown INSTALL_MODE '$INSTALL_MODE', using link.${NC}"
        MODE_ARG="--link"
        ;;
esac

"$INSTALL_DIR/scripts/install.sh" "$MODE_ARG" --apply
