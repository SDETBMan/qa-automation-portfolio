Generate an automated test based on this description: $ARGUMENTS

Steps:
1. Find the relevant test directory and read existing tests to learn conventions (fixtures, naming, assertions, imports)
2. Read the source code under test to understand function signatures and data models
3. Generate a test file that follows the project's existing patterns exactly
4. Validate syntax with `python -m py_compile` or equivalent
5. Run the test to verify it passes
6. Iterate on failures until green

The generated test must be indistinguishable from hand-written tests in the project.
