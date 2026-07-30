Review the test files in $ARGUMENTS for QA engineering best practices.

Check for:
- Page Object Model violations (raw selectors in test files, assertions in page objects)
- Wait strategy issues (hard waits without justification, manual polling)
- Test isolation problems (shared mutable state, execution order dependencies)
- Assertion quality (weak messages, snapshot vs retrying assertions)
- Data management (hard-coded test data, UI-based data creation)
- Fixture hygiene (duplicated setup, missing cleanup)

For each finding, cite the file and line, explain why it's a problem, and show the fix.
