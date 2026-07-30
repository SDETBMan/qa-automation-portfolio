Analyze the JUnit XML test results in $ARGUMENTS (or the most recent CI run) and produce a failure triage report.

For each failing test:
1. Read the failure message and stack trace
2. Categorize the root cause (assertion error, element not found, timeout, setup failure, API error, data error)
3. Group failures by root cause
4. For each group: count affected tests, assess severity, suggest a fix action

Output a structured triage report sorted by severity, with the highest-impact cluster first.
