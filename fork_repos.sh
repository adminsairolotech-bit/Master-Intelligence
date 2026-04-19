#!/bin/bash
# Fork/Organize SAI Rolotech Repos by Category
# Usage: ./fork_repos.sh [action] [repo-name]
# Actions: list, fork, status

set -e

GITHUB_USER="adminsairolotech-bit"
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
echo_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Category mapping with new repo names
declare -A REPO_MAP=(
    # AI Agents & Automation
    ["agno-multiagent"]="agno-multiagent-sairolotech"
    ["sai-rolotech-ai-hub"]="sai-rolotech-ai-hub"
    ["sai-rolotech-pro-ai"]="sai-rolotech-pro-ai"
    ["sai-rolotech-openclaw"]="sai-rolotech-openclaw"

    # AI Tools & Extensions
    ["prompt-builder-vscode"]="prompt-builder-vscode"
    ["sai-rolotech-prompts"]="sai-rolotech-prompts"
    ["Agentfy"]="sai-rolotech-agentfy"

    # Roll Forming Engineering
    ["autocad-bridge"]="sai-rolotech-autocad"
    ["sai-rolotech-autocad"]="sai-rolotech-autocad"
    ["sai-rolotech-engine"]="sai-rolotech-engine"

    # Cloud & Infrastructure
    ["cloud-ai"]="sai-rolotech-cloud-ai"
    ["sai-rolotech-n8n"]="sai-rolotech-n8n"
    ["openclaw-bridge"]="sai-rolotech-openclaw-bridge"

    # Social Media & Marketing
    ["instagram-ai"]="sai-rolotech-instagram-ai"
    ["instagram-automation"]="sai-rolotech-instagram-automation"
    ["Prompt-Builder-Chatbot"]="sai-rolotech-chatbot"

    # Development Tools
    ["ai-command-center"]="sai-rolotech-command-center"
    ["ai-agent"]="sai-rolotech-ai-agent"
)

# Category descriptions
declare -A CATEGORY_MAP=(
    ["agno-multiagent"]="AI Agents & Automation"
    ["sai-rolotech-ai-hub"]="AI Agents & Automation"
    ["sai-rolotech-pro-ai"]="AI Agents & Automation"
    ["sai-rolotech-openclaw"]="AI Agents & Automation"
    ["prompt-builder-vscode"]="AI Tools & Extensions"
    ["sai-rolotech-prompts"]="AI Tools & Extensions"
    ["Agentfy"]="AI Agents & Automation"
    ["autocad-bridge"]="Roll Forming Engineering"
    ["sai-rolotech-autocad"]="Roll Forming Engineering"
    ["sai-rolotech-engine"]="Roll Forming Engineering"
    ["cloud-ai"]="Cloud & Infrastructure"
    ["sai-rolotech-n8n"]="Cloud & Infrastructure"
    ["openclaw-bridge"]="Cloud & Infrastructure"
    ["instagram-ai"]="Social Media & Marketing"
    ["instagram-automation"]="Social Media & Marketing"
    ["Prompt-Builder-Chatbot"]="Social Media & Marketing"
    ["ai-command-center"]="Development Tools"
    ["ai-agent"]="Development Tools"
)

show_help() {
    cat << EOF
${GREEN}SAI ROLO TECH - Repo Fork Manager${NC}

${YELLOW}Usage:${NC}
    ./fork_repos.sh <command> [options]

${YELLOW}Commands:${NC}
    list                    List all repos by category
    status                  Check which repos are on GitHub
    fork <repo-name>        Fork/push a specific repo
    fork-all                Fork all repos to GitHub
    sync <repo-name>        Sync local changes to GitHub

${YELLOW}Examples:${NC}
    ./fork_repos.sh list
    ./fork_repos.sh status
    ./fork_repos.sh fork agno-multiagent
    ./fork_repos.sh fork-all

${YELLOW}Categories:${NC}
    🤖 AI Agents & Automation
    🔌 AI Tools & Extensions
    🏭 Roll Forming Engineering
    ☁️ Cloud & Infrastructure
    📱 Social Media & Marketing
    🛠️ Development Tools

EOF
}

list_repos() {
    echo -e "\n${GREEN}=== SAI ROLO TECH REPOS BY CATEGORY ===${NC}\n"

    local current_category=""
    for dir in "${!REPO_MAP[@]}"; do
        category="${CATEGORY_MAP[$dir]}"
        if [[ "$category" != "$current_category" ]]; then
            echo -e "\n${YELLOW}### $category ###${NC}"
            current_category="$category"
        fi
        echo "  📁 $dir → ${REPO_MAP[$dir]}"
    done
}

check_status() {
    echo -e "\n${GREEN}=== REPO STATUS CHECK ===${NC}\n"

    for dir in "${!REPO_MAP[@]}"; do
        if [[ -d "$BASE_DIR/$dir" ]]; then
            local gh_repo="${REPO_MAP[$dir]}"
            if gh repo view "$GITHUB_USER/$gh_repo" &>/dev/null; then
                echo -e "${GREEN}✓${NC} $dir → $gh_repo (EXISTS)"
            else
                echo -e "${YELLOW}○${NC} $dir → $gh_repo (NOT ON GITHUB)"
            fi
        else
            echo -e "${RED}✗${NC} $dir (LOCAL NOT FOUND)"
        fi
    done
}

fork_repo() {
    local dir="$1"
    local gh_repo="${REPO_MAP[$dir]}"

    if [[ -z "$gh_repo" ]]; then
        echo_error "Unknown repo: $dir"
        exit 1
    fi

    if [[ ! -d "$BASE_DIR/$dir" ]]; then
        echo_error "Directory not found: $dir"
        exit 1
    fi

    echo_info "Forking $dir → $gh_repo"

    cd "$BASE_DIR/$dir"

    # Check if already exists on GitHub
    if gh repo view "$GITHUB_USER/$gh_repo" &>/dev/null; then
        echo_warn "Repo already exists on GitHub: $gh_repo"
        echo_info "Syncing local changes..."

        # Add remote if needed
        if ! git remote get-url origin &>/dev/null 2>&1; then
            git remote add origin "https://github.com/$GITHUB_USER/$gh_repo.git"
        else
            git remote set-url origin "https://github.com/$GITHUB_USER/$gh_repo.git"
        fi

        git add -A
        git commit -m "Update $(date '+%Y-%m-%d %H:%M')" || true
        git push -u origin main --force 2>/dev/null || git push -u origin master --force
        echo_success "Synced!"
    else
        # Create new repo
        echo_info "Creating new repo: $gh_repo"

        # Initialize git if not
        if [[ ! -d ".git" ]]; then
            git init
            git add -A
            git commit -m "Initial commit - $(date '+%Y-%m-%d')"
        fi

        # Create GitHub repo
        gh repo create "$gh_repo" --public --source=. --push

        echo_success "Created: https://github.com/$GITHUB_USER/$gh_repo"
    fi

    cd "$BASE_DIR"
}

fork_all() {
    echo_info "Forking all repos..."

    for dir in "${!REPO_MAP[@]}"; do
        if [[ -d "$BASE_DIR/$dir" ]]; then
            echo ""
            fork_repo "$dir"
            sleep 2  # Rate limiting
        fi
    done

    echo_success "All repos forked!"
}

sync_repo() {
    local dir="$1"
    fork_repo "$dir"
}

# Main
case "${1:-}" in
    list)
        list_repos
        ;;
    status)
        check_status
        ;;
    fork)
        if [[ -z "$2" ]]; then
            echo_error "Usage: $0 fork <repo-name>"
            exit 1
        fi
        fork_repo "$2"
        ;;
    fork-all)
        fork_all
        ;;
    sync)
        if [[ -z "$2" ]]; then
            echo_error "Usage: $0 sync <repo-name>"
            exit 1
        fi
        sync_repo "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac
