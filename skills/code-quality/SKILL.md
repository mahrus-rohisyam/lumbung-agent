---
name: code-quality
description: Review or improve code quality, architecture, readability, error handling, edge cases, and testability before merging. Use when refactoring, reviewing a PR/diff, or checking that new code is clean, maintainable, and idiomatic.
---

# Code quality

Ensure code is correct, clear to the next engineer, and easy to change without breaking unrelated behavior. Review the changed code and its immediate call sites.

## 1. Correctness & edge cases

- **Boundaries:** Empty collections, `null`/`nil`/`undefined`, zero/negative numbers, max lengths, concurrent access, and partial failures.
- **State & invariants:** Illegal states should be unrepresentable or rejected at the boundary; validate inputs once at entry.
- **Error handling:** Errors are handled or propagated with clear context; no silent failures, and cleanup/resources (`close`, `defer`, `finally`, transactions) are guaranteed on error paths.

## 2. Design & modularity

- **Single responsibility:** Functions and modules do one cohesive job with shallow nesting and early returns.
- **Right-sized abstractions:** Extract shared logic when duplicated meaningfully; avoid premature interfaces, wrappers, or over-engineered patterns for single-use code.
- **Uniformity:** Handle variants via data structures/tables or shared paths instead of sprawling `if/else` chains.
- **Reuse:** Use existing project utilities and standard library primitives instead of re-implementing them.

## 3. Readability & maintainability

- **Naming:** Identifiers reflect domain concepts and intent; avoid vague names (`data`, `info`, `temp`, `handle`) and inconsistent synonyms.
- **Comments & docs:** Public APIs have concise docstrings; inline comments explain *why* (constraints, invariants, trade-offs), not *what* the code already says.
- **Dead code:** Remove unused imports, variables, unreachable branches, and stale feature flags.

## 4. Performance & reliability

- **Query & I/O patterns:** Watch for N+1 queries, unbounded loops/fetches, missing pagination, and missing timeouts on network/DB calls.
- **Concurrency:** Avoid shared mutable state without synchronization; ensure background tasks have cancellation and shutdown paths.

## 5. Testability & verification

- **Behavior over implementation:** Tests assert observable outcomes and contracts, not internal mock call counts.
- **Coverage of paths:** Include happy path, invalid input, permission/boundary failure, and regression cases for bug fixes.
- **Reproducible checks:** Run the project's formatter, linter, typechecker, and test suite after edits.

## Output

For a review, report findings as `path:line: category — issue and concrete fix`, ordered by severity (correctness/bugs first, then design/readability). Note what tests/checks were run.
