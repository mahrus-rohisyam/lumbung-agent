---
name: code-slop
description: Find and remove AI-slop patterns in code before a change is reported as done. Use on every finished code change, when reviewing AI-written code, or when the user asks whether code looks generated. Covers noise comments, speculative abstractions, defensive code for impossible states, swallowed errors, invented APIs, duplicated existing functionality and padded tests. For prose (docs, commit messages, UI copy), use no-ai-slop instead.
---

# Code slop

Slop is code that looks complete but is longer, vaguer or less correct than it needs to be. Review the diff, not the whole repo. Each finding needs a file, a line and a concrete fix.

## Patterns

**Comments**
- Comments that restate the code (`// increment counter`, `// Helper function to get user`).
- Change-log comments (`// Updated to fix bug`, `// New implementation`, `// Added for X`).
- Section banners, emoji, and "Note:" / "Important:" prefixes.
- Commented-out code, and TODOs without an issue reference.
- Keep comments that say *why*: a constraint, a non-obvious invariant, a link to an incident.

**Structure**
- An interface or abstract base class with one implementation, defined next to that implementation. Define abstractions where consumed, and only when multiple implementations or a test seam require one.
- Factories, managers, services, wrappers and option structs that add a layer without a second user.
- Grab-bag modules or folders named `utils`, `helpers`, `common`, `misc`.
- Config flags, parameters or generic type parameters nobody asked for.
- Re-implementing something the project's shared modules or the standard library already provides.

**Errors and control flow**
- Checks for states the types or the caller already rule out.
- Errors swallowed or logged and then ignored (e.g. empty `catch {}`, bare `except: pass`, discarded error returns). Wrap errors with context when propagating.
- `panic` / unhandled throws in library code, import-time side effects (`init()`), module-level mutable state.
- Background tasks or goroutines without an owner, cancellation context and a way to stop (e.g. `context.Background()` inside a request handler).

**Invented or stale APIs**
- Functions, options or flags that do not exist at the pinned version. Verify against the installed package docs or type definitions (see `dependency-check`).

**TypeScript / Frontend (when applicable)**
- `any`, `as unknown as T`, `@ts-ignore` / `@ts-expect-error` without a reason.
- `useEffect` that derives state from props or other state; compute it during render.
- `useMemo` / `useCallback` everywhere without a measured reason.
- Wrapper components that only forward props to one child.
- Debug logging left in (`console.log`, `print`, `fmt.Println`), and ad-hoc API calls bypassing the project's API client.

**Tests**
- Tests that assert the mock was called instead of the behavior.
- Many near-identical tests where one parameterized / table-driven test would do.
- Snapshot tests of large output nobody will review.
- Missing the negative case: wrong user, invalid input, empty list.

**Naming**
- Vague names (`data`, `result`, `info`, `item`, `handleStuff`) where a domain word exists.
- Stacked suffixes (`UserServiceManagerImpl`).
- Synonym cycling: the same thing called `account`, `user` and `member` in one change.

**Logs and messages**
- Log lines on every step, emoji in logs, or messages that leak internals to users.
- Error messages for users: say what happened and what to do, in plain words.

## Deterministic pre-check

Run `python3 "${PLUGIN_ROOT}/scripts/clean_unicode.py" --diff` (fallback: `${CLAUDE_PLUGIN_ROOT}` or `~/lumbung-agent`) to catch invisible Unicode watermarks, bidi controls, and non-ASCII spaces before manual review. Pass `--fix` when cleaning your own diff (add `--ascii-punct` for code files with smart quotes or stray dashes).

## Size check

Compare the diff to the request. If the change adds more than it needs, cut it. Each changed line should trace back to the request.

## Output

For a review, list findings as `path:line: pattern, fix`. When you fix your own diff, fix first, then report only what changed. Do not rewrite code outside the diff.
