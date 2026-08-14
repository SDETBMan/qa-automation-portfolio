#!/usr/bin/env bash
# ── check-assertions.sh — Zero-assertion test detector ───────────────────────
# Scans changed test files for test functions/methods that contain zero
# assertions. Tests with zero assertions always pass regardless of app
# behavior, which defeats the purpose of the test.
#
# Usage:
#   bash .claude/skills/verify-changes/scripts/check-assertions.sh
#
# Exit codes:
#   0 — No zero-assertion tests found (or no test files changed)
#   1 — At least one zero-assertion test detected
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

# ── Find changed test files ──────────────────────────────────────────────────
DIFF_FILES=$(git diff --name-only HEAD 2>/dev/null || git diff --name-only)

if [[ -z "$DIFF_FILES" ]]; then
    echo "ASSERTION CHECK: No changes detected — nothing to check."
    exit 0
fi

# Collect changed test files matching known patterns
declare -a TEST_FILES=()

while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    case "$file" in
        cypress/cypress/e2e/*.cy.ts)                    TEST_FILES+=("$file") ;;
        selenium-java/src/test/**/tests/*Test.java)     TEST_FILES+=("$file") ;;
        selenium-java/src/test/*/tests/*Test.java)      TEST_FILES+=("$file") ;;
        cucumber/src/test/**/stepDefinitions/*Steps.java) TEST_FILES+=("$file") ;;
        cucumber/src/test/*/stepDefinitions/*Steps.java)  TEST_FILES+=("$file") ;;
        cucumber_python/features/steps/*.py)             TEST_FILES+=("$file") ;;
        playwright/tests/Framework.Tests/Tests/*Test.cs) TEST_FILES+=("$file") ;;
        playwright/tests/playwright-ts/tests/*.spec.ts)  TEST_FILES+=("$file") ;;
    esac

    # Python pytest: **/tests/test_*.py
    if [[ "$file" =~ tests/test_.*\.py$ ]]; then
        if [[ "$file" != cucumber_python/* ]]; then
            local_found=0
            for existing in "${TEST_FILES[@]+"${TEST_FILES[@]}"}"; do
                [[ "$existing" == "$file" ]] && { local_found=1; break; }
            done
            [[ $local_found -eq 0 ]] && TEST_FILES+=("$file")
        fi
    fi
done <<< "$DIFF_FILES"

if [[ ${#TEST_FILES[@]} -eq 0 ]]; then
    echo "ASSERTION CHECK: No test files changed — nothing to check."
    exit 0
fi

echo "ASSERTION CHECK: Scanning ${#TEST_FILES[@]} changed test file(s):"
for f in "${TEST_FILES[@]}"; do
    echo "  $f"
done
echo

# ── Framework detection ──────────────────────────────────────────────────────
get_framework() {
    local file="$1"
    case "$file" in
        cypress/*)                                echo "cypress" ;;
        selenium-java/*)                          echo "selenium-java" ;;
        cucumber/src/test/*stepDefinitions*)       echo "cucumber-java" ;;
        cucumber_python/*)                        echo "cucumber-python" ;;
        playwright/tests/Framework.Tests/*)       echo "playwright-csharp" ;;
        playwright/tests/playwright-ts/*)         echo "playwright-ts" ;;
        *)
            [[ "$file" =~ \.py$ ]] && echo "pytest" || echo "unknown"
            ;;
    esac
}

# ── Count braces in a string using bash builtins ─────────────────────────────
count_char() {
    local str="$1" ch="$2"
    local stripped="${str//[^$ch]/}"
    echo ${#stripped}
}

# ── Assertion checking per framework ─────────────────────────────────────────
# Uses bash built-in [[ =~ ]] regex matching to avoid forking grep per line.
FOUND_ISSUES=0
TOTAL_TESTS=0

check_brace_language() {
    # Generic brace-based test body checker.
    # $1 = file, $2 = start pattern regex, $3 = assertion regex, $4 = name extraction mode
    local file="$1"
    local start_re="$2"
    local assert_re="$3"
    local name_mode="$4"

    local in_test=0 brace_depth=0 test_name="" test_line=0 has_assertion=0 line_num=0

    while IFS= read -r line; do
        # Strip trailing carriage return (Windows line endings)
        line="${line%$'\r'}"
        line_num=$((line_num + 1))

        # Detect start of test
        if [[ $in_test -eq 0 ]] && [[ "$line" =~ $start_re ]]; then
            in_test=1
            brace_depth=0
            has_assertion=0
            test_line=$line_num

            # Extract test name based on mode
            case "$name_mode" in
                js-it)
                    # it('name' or test('name'
                    if [[ "$line" =~ (it|test)\([\'\"](.*)[\'\"]\, ]]; then
                        test_name="${BASH_REMATCH[2]:0:80}"
                    else
                        test_name="(unnamed)"
                    fi
                    ;;
                java-void)
                    # public void methodName(
                    if [[ "$line" =~ void[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*) ]]; then
                        test_name="${BASH_REMATCH[1]}"
                    else
                        test_name="(unnamed)"
                    fi
                    ;;
                csharp-task)
                    # public async Task MethodName(
                    if [[ "$line" =~ (Task|void)[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*) ]]; then
                        test_name="${BASH_REMATCH[2]}"
                    else
                        test_name="(unnamed)"
                    fi
                    ;;
            esac
        fi

        if [[ $in_test -eq 1 ]]; then
            # Count braces using bash builtins
            local opens=${line//[^\{]/}
            local closes=${line//[^\}]/}
            brace_depth=$((brace_depth + ${#opens} - ${#closes}))

            # Check for assertions
            if [[ "$line" =~ $assert_re ]]; then
                has_assertion=1
            fi

            # End of test block: depth returned to 0 (or below) after entering body
            if [[ $brace_depth -le 0 && $line_num -gt $test_line ]]; then
                TOTAL_TESTS=$((TOTAL_TESTS + 1))
                if [[ $has_assertion -eq 0 ]]; then
                    echo "  WARN  $file:$test_line — \"$test_name\" has zero assertions"
                    FOUND_ISSUES=$((FOUND_ISSUES + 1))
                fi
                in_test=0
            fi
        fi
    done < "$file"
}

check_cypress_ts() {
    check_brace_language "$1" \
        '^[[:space:]]*(it|test)\(' \
        '\.should\(|expect\(' \
        "js-it"
}

check_java_test() {
    # Two-pass: first find @Test lines, then check the method body
    local file="$1"
    local in_test=0 brace_depth=0 test_name="" test_line=0 has_assertion=0 line_num=0
    local found_annotation=0

    while IFS= read -r line; do
        line="${line%$'\r'}"
        line_num=$((line_num + 1))

        # Detect @Test annotation
        if [[ "$line" =~ ^[[:space:]]*@Test ]]; then
            found_annotation=1
            continue
        fi

        # After @Test, look for method signature
        if [[ $found_annotation -eq 1 ]]; then
            if [[ "$line" =~ public[[:space:]]+void[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*) ]]; then
                in_test=1
                brace_depth=0
                test_name="${BASH_REMATCH[1]}"
                test_line=$line_num
                has_assertion=0
                found_annotation=0
            elif [[ ! "$line" =~ ^[[:space:]]*(@|$|//) ]]; then
                found_annotation=0
            fi
        fi

        if [[ $in_test -eq 1 ]]; then
            local opens=${line//[^\{]/}
            local closes=${line//[^\}]/}
            brace_depth=$((brace_depth + ${#opens} - ${#closes}))

            if [[ "$line" =~ Assert\. ]]; then
                has_assertion=1
            fi

            if [[ $brace_depth -le 0 && $line_num -gt $test_line ]]; then
                TOTAL_TESTS=$((TOTAL_TESTS + 1))
                if [[ $has_assertion -eq 0 ]]; then
                    echo "  WARN  $file:$test_line — \"$test_name\" has zero assertions"
                    FOUND_ISSUES=$((FOUND_ISSUES + 1))
                fi
                in_test=0
            fi
        fi
    done < "$file"
}

check_cucumber_java_then() {
    # Only check @Then methods — @Given/@When are action steps
    local file="$1"
    local in_then=0 brace_depth=0 test_name="" test_line=0 has_assertion=0 line_num=0
    local found_annotation=0

    while IFS= read -r line; do
        line="${line%$'\r'}"
        line_num=$((line_num + 1))

        if [[ "$line" =~ ^[[:space:]]*@Then ]]; then
            found_annotation=1
            if [[ "$line" =~ @Then\([\"\'](.*)[\"\']\) ]]; then
                test_name="${BASH_REMATCH[1]:0:80}"
            else
                test_name="(unnamed)"
            fi
            test_line=$line_num
            continue
        fi

        if [[ $found_annotation -eq 1 ]]; then
            if [[ "$line" =~ public[[:space:]]+void[[:space:]]+[a-zA-Z_] ]]; then
                in_then=1
                brace_depth=0
                has_assertion=0
                found_annotation=0
            elif [[ ! "$line" =~ ^[[:space:]]*(@|$|//) ]]; then
                found_annotation=0
            fi
        fi

        if [[ $in_then -eq 1 ]]; then
            local opens=${line//[^\{]/}
            local closes=${line//[^\}]/}
            brace_depth=$((brace_depth + ${#opens} - ${#closes}))

            [[ "$line" =~ Assert\. ]] && has_assertion=1

            if [[ $brace_depth -le 0 && $line_num -gt $test_line ]]; then
                TOTAL_TESTS=$((TOTAL_TESTS + 1))
                if [[ $has_assertion -eq 0 ]]; then
                    echo "  WARN  $file:$test_line — @Then \"$test_name\" has zero assertions"
                    FOUND_ISSUES=$((FOUND_ISSUES + 1))
                fi
                in_then=0
            fi
        fi
    done < "$file"
}

check_cucumber_python_then() {
    # Only check @then functions
    local file="$1"
    local in_then=0 test_name="" test_line=0 has_assertion=0 line_num=0
    local found_decorator=0

    while IFS= read -r line; do
        line="${line%$'\r'}"
        line_num=$((line_num + 1))

        if [[ "$line" =~ ^[[:space:]]*@then ]]; then
            found_decorator=1
            if [[ "$line" =~ @then\([\"\'](.*)[\"\']\) ]]; then
                test_name="${BASH_REMATCH[1]:0:80}"
            else
                test_name="(unnamed)"
            fi
            test_line=$line_num
            continue
        fi

        if [[ $found_decorator -eq 1 ]]; then
            if [[ "$line" =~ ^def[[:space:]]+[a-zA-Z_] ]]; then
                in_then=1
                has_assertion=0
                found_decorator=0
            fi
        fi

        if [[ $in_then -eq 1 && $line_num -gt $((test_line + 1)) ]]; then
            # Python function ends at next top-level def/decorator/class
            if [[ "$line" =~ ^(def[[:space:]]|@|class[[:space:]]) ]]; then
                TOTAL_TESTS=$((TOTAL_TESTS + 1))
                if [[ $has_assertion -eq 0 ]]; then
                    echo "  WARN  $file:$test_line — @then \"$test_name\" has zero assertions"
                    FOUND_ISSUES=$((FOUND_ISSUES + 1))
                fi
                in_then=0
                # Check if this starts a new @then
                if [[ "$line" =~ ^[[:space:]]*@then ]]; then
                    found_decorator=1
                    if [[ "$line" =~ @then\([\"\'](.*)[\"\']\) ]]; then
                        test_name="${BASH_REMATCH[1]:0:80}"
                    else
                        test_name="(unnamed)"
                    fi
                    test_line=$line_num
                fi
                continue
            fi

            [[ "$line" =~ [[:space:]]assert[[:space:]] || "$line" =~ ^[[:space:]]*assert[[:space:]] ]] && has_assertion=1
        fi
    done < "$file"

    # Handle last function in file
    if [[ $in_then -eq 1 ]]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if [[ $has_assertion -eq 0 ]]; then
            echo "  WARN  $file:$test_line — @then \"$test_name\" has zero assertions"
            FOUND_ISSUES=$((FOUND_ISSUES + 1))
        fi
    fi
}

check_playwright_csharp() {
    local file="$1"
    local in_test=0 brace_depth=0 test_name="" test_line=0 has_assertion=0 line_num=0
    local found_attribute=0

    while IFS= read -r line; do
        line="${line%$'\r'}"
        line_num=$((line_num + 1))

        if [[ "$line" =~ ^[[:space:]]*\[Test\] ]]; then
            found_attribute=1
            continue
        fi

        if [[ $found_attribute -eq 1 ]]; then
            if [[ "$line" =~ (Task|void)[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*) ]]; then
                in_test=1
                brace_depth=0
                test_name="${BASH_REMATCH[2]}"
                test_line=$line_num
                has_assertion=0
                found_attribute=0
            elif [[ ! "$line" =~ ^[[:space:]]*(\[|$|//) ]]; then
                found_attribute=0
            fi
        fi

        if [[ $in_test -eq 1 ]]; then
            local opens=${line//[^\{]/}
            local closes=${line//[^\}]/}
            brace_depth=$((brace_depth + ${#opens} - ${#closes}))

            [[ "$line" =~ Assert\.That\( ]] && has_assertion=1

            if [[ $brace_depth -le 0 && $line_num -gt $test_line ]]; then
                TOTAL_TESTS=$((TOTAL_TESTS + 1))
                if [[ $has_assertion -eq 0 ]]; then
                    echo "  WARN  $file:$test_line — \"$test_name\" has zero assertions"
                    FOUND_ISSUES=$((FOUND_ISSUES + 1))
                fi
                in_test=0
            fi
        fi
    done < "$file"
}

check_playwright_ts() {
    check_cypress_ts "$1"
}

check_pytest() {
    local file="$1"
    local in_test=0 test_name="" test_line=0 has_assertion=0 line_num=0

    while IFS= read -r line; do
        line="${line%$'\r'}"
        line_num=$((line_num + 1))

        if [[ "$line" =~ ^[[:space:]]*def[[:space:]]+(test_[a-zA-Z0-9_]+) ]]; then
            # Finalize previous test if any
            if [[ $in_test -eq 1 ]]; then
                TOTAL_TESTS=$((TOTAL_TESTS + 1))
                if [[ $has_assertion -eq 0 ]]; then
                    echo "  WARN  $file:$test_line — \"$test_name\" has zero assertions"
                    FOUND_ISSUES=$((FOUND_ISSUES + 1))
                fi
            fi
            in_test=1
            test_name="${BASH_REMATCH[1]}"
            test_line=$line_num
            has_assertion=0
            continue
        fi

        if [[ $in_test -eq 1 ]]; then
            # End of function: top-level def, class, or decorator
            if [[ "$line" =~ ^(def[[:space:]]|class[[:space:]]|@) ]] && [[ $line_num -gt $((test_line + 1)) ]]; then
                TOTAL_TESTS=$((TOTAL_TESTS + 1))
                if [[ $has_assertion -eq 0 ]]; then
                    echo "  WARN  $file:$test_line — \"$test_name\" has zero assertions"
                    FOUND_ISSUES=$((FOUND_ISSUES + 1))
                fi
                in_test=0
                continue
            fi

            [[ "$line" =~ [[:space:]]assert[[:space:]] || "$line" =~ ^[[:space:]]*assert[[:space:]] ]] && has_assertion=1
        fi
    done < "$file"

    # Handle last function in file
    if [[ $in_test -eq 1 ]]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if [[ $has_assertion -eq 0 ]]; then
            echo "  WARN  $file:$test_line — \"$test_name\" has zero assertions"
            FOUND_ISSUES=$((FOUND_ISSUES + 1))
        fi
    fi
}

# ── Process each test file ───────────────────────────────────────────────────
echo "── Checking for zero-assertion tests ──────────────────────"
echo

for file in "${TEST_FILES[@]}"; do
    [[ ! -f "$file" ]] && continue
    framework=$(get_framework "$file")

    case "$framework" in
        cypress)            check_cypress_ts "$file" ;;
        selenium-java)      check_java_test "$file" ;;
        cucumber-java)      check_cucumber_java_then "$file" ;;
        cucumber-python)    check_cucumber_python_then "$file" ;;
        playwright-csharp)  check_playwright_csharp "$file" ;;
        playwright-ts)      check_playwright_ts "$file" ;;
        pytest)             check_pytest "$file" ;;
        *)                  echo "  SKIP  $file (unknown framework)" ;;
    esac
done

# ── Summary ──────────────────────────────────────────────────────────────────
echo
echo "── Summary ──────────────────────────────────────────────────"
echo "  Tests scanned: $TOTAL_TESTS"
echo "  Zero-assertion tests: $FOUND_ISSUES"

if [[ $FOUND_ISSUES -gt 0 ]]; then
    echo
    echo "NOTE: Tests that delegate assertions to page object methods"
    echo "(e.g., loginPage.isLoginButtonVisible() which internally calls"
    echo ".should('exist')) will appear assertion-free at the test level."
    echo "Review each warning to determine if the delegation is intentional."
fi

exit $( [[ $FOUND_ISSUES -gt 0 ]] && echo 1 || echo 0 )
