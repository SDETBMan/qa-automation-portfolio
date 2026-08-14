#!/usr/bin/env bash
# ── Verification skill: framework detection + test runner ────────────────────
# Usage:
#   check.sh --detect              List affected frameworks from git diff
#   check.sh --run <framework>     Run tests for a specific framework
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

# ── Framework → test command mapping ─────────────────────────────────────────
# Uses bash 5.2 associative arrays. Values are the shell commands to run tests.
# "SKIP:<reason>" means no automated test suite to run.
# "LINT:<command>" means lint/validate only (no test execution).
declare -A COMMANDS=(
    # Browser / E2E
    [cypress]="cd cypress && npm ci --quiet && npm test"
    [playwright]="cd playwright && dotnet test"
    [selenium-java]="cd selenium-java && mvn clean test -Dheadless=true"

    # BDD
    [cucumber]="cd cucumber && mvn clean test -Dheadless=true"
    [cucumber_python]="cd cucumber_python && pip install -r requirements.txt -q && HEADLESS=true python -m behave --no-capture"

    # API / Service
    [postman]="cd postman && npm ci --quiet && npm test"
    [fastapi-service]="cd fastapi-service && pip install -r requirements.txt -q && python -m pytest tests/ -v --cov=app --cov-report=term-missing"
    [pact-consumer]="cd pact-consumer && npm ci --quiet && npm test"

    # LLM Evaluation
    [ai-eval]="cd ai-eval && pip install -r requirements.txt -q && python -m pytest -v"
    [conv-eval]="cd conv-eval && pip install -r requirements.txt -q && python -m pytest -v"
    [agent-eval]="cd agent-eval && pip install -r requirements.txt -q && python -m pytest -v"

    # AI Agents
    [job-agent]="SKIP:Requires ANTHROPIC_API_KEY and TAVILY_API_KEY"
    [coding-agent]="SKIP:Requires ANTHROPIC_API_KEY"
    [failure-triage]="SKIP:Requires ANTHROPIC_API_KEY"

    # LLM Frameworks
    [langchain-rag]="SKIP:Requires OPENAI_API_KEY"
    [langgraph-agent]="SKIP:Requires ANTHROPIC_API_KEY"
    [dspy-optimizer]="SKIP:Requires OPENAI_API_KEY"
    [dspy-vertex]="SKIP:Requires Vertex AI credentials"

    # Data & Analytics
    [claims-diff]="cd claims-diff && pip install -r requirements.txt -q && python -m pytest tests/ -v --cov=differ --cov-report=term-missing"
    [flakiness-detector]="cd flakiness-detector && pip install -r requirements.txt -q && python -m pytest tests/ -v"
    [quality-dashboard]="SKIP:Requires DD_API_KEY and GitHub token"
    [site-monitor]="cd site-monitor && pip install -r requirements.txt -q && python run.py"
    [vulnerability-aggregator]="SKIP:Requires gh CLI authenticated"
    [dependency-audit]="cd dependency-audit && pip install -r requirements.txt -q && python run.py --help > /dev/null"

    # QMS & Compliance
    [qms-evidence-collector]="SKIP:Requires DD_API_KEY"

    # Infrastructure
    [terraform]="LINT:cd terraform && terraform fmt -check -recursive"
    [k8s]="LINT:cd k8s && kubectl apply --dry-run=client -f namespace.yaml -f configmap.yaml"
)

# ── Detect mode ──────────────────────────────────────────────────────────────
detect() {
    local changed_dirs
    changed_dirs=$(git diff --name-only HEAD 2>/dev/null || git diff --name-only)

    if [[ -z "$changed_dirs" ]]; then
        echo "No changes detected."
        return 0
    fi

    # Extract unique top-level directories, filter to known frameworks
    local frameworks=()
    while IFS= read -r dir; do
        if [[ -n "${COMMANDS[$dir]+exists}" ]]; then
            frameworks+=("$dir")
        fi
    done < <(echo "$changed_dirs" | sed 's|/.*||' | sort -u)

    if [[ ${#frameworks[@]} -eq 0 ]]; then
        echo "Changes detected but no known framework directories affected."
        echo "Changed paths:"
        echo "$changed_dirs" | sed 's/^/  /'
        return 0
    fi

    echo "Affected frameworks:"
    for fw in "${frameworks[@]}"; do
        local cmd="${COMMANDS[$fw]}"
        local status="test"
        if [[ "$cmd" == SKIP:* ]]; then
            status="skip (${cmd#SKIP:})"
        elif [[ "$cmd" == LINT:* ]]; then
            status="lint only"
        fi
        echo "  $fw [$status]"
    done
}

# ── Run mode ─────────────────────────────────────────────────────────────────
run() {
    local framework="$1"

    if [[ -z "${COMMANDS[$framework]+exists}" ]]; then
        echo "ERROR: Unknown framework '$framework'"
        echo "Known frameworks: ${!COMMANDS[*]}"
        return 1
    fi

    local cmd="${COMMANDS[$framework]}"

    if [[ "$cmd" == SKIP:* ]]; then
        echo "SKIP [$framework]: ${cmd#SKIP:}"
        return 0
    fi

    if [[ "$cmd" == LINT:* ]]; then
        cmd="${cmd#LINT:}"
        echo "LINT [$framework]: $cmd"
    else
        echo "TEST [$framework]: $cmd"
    fi

    echo "──────────────────────────────────────────────────"
    eval "$cmd"
    local exit_code=$?
    echo "──────────────────────────────────────────────────"

    if [[ $exit_code -eq 0 ]]; then
        echo "PASS [$framework]"
    else
        echo "FAIL [$framework] (exit code $exit_code)"
    fi

    return $exit_code
}

# ── Main ─────────────────────────────────────────────────────────────────────
case "${1:-}" in
    --detect)
        detect
        ;;
    --run)
        if [[ -z "${2:-}" ]]; then
            echo "Usage: check.sh --run <framework>"
            echo "Known frameworks: ${!COMMANDS[*]}"
            exit 1
        fi
        run "$2"
        ;;
    *)
        echo "Usage:"
        echo "  check.sh --detect              Detect affected frameworks"
        echo "  check.sh --run <framework>     Run tests for a framework"
        exit 1
        ;;
esac
