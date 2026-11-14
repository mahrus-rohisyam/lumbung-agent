# Troubleshooting

## A new agent from another machine does not show up

1. Agents load at session start, and the update is pulled at session start, so open one more new session.
2. Check the clone: `git -C ~/lumbung status` (`$HOME\lumbung` on Windows).
   - Not on `master`: develop mode, no updates. Switch back with `git switch master`, then run `python install.py`.
   - "Your branch and 'origin/master' have diverged": local commits that were never pushed. Rebase or merge them by hand, push, then run `python install.py`.
3. Check that git can reach the remote without a prompt: `git -C ~/lumbung fetch origin`. If it asks for a password, sync cannot work. Set up an SSH key or credential helper ([setup.md](setup.md#requirements)).
4. Was it pushed? On the machine that made it: `git log origin/master -1`.

## The guard blocked an agent that is not a duplicate

Read the message: it names the matching agent and the shared terms.

- If the other agent really covers it, extend that one instead.
- If the match is wrong, make the new description more specific. Shared generic words like "review" or "change" add up quickly.
- If it is a real, intended second version, add `# lumbung-override: <reason>` to the frontmatter and a registry row.

If it misfires often, raise `THRESHOLD` or `MIN_SHARED` in `hooks/guard_agent.py`, or add the noisy word to `STOP`.

## "is installed from Lumbung and will be overwritten"

You, or Claude, tried to edit `~/.claude/agents/<name>.md`. Edit `lumbung/agents/<name>.md` instead, then run `install.py`.

## Sessions start slowly

Sync waits at most 8 s for `git fetch`. If the remote is unreachable, the fetch should fail fast. It is slow when DNS or SSH hangs: for example, when the VM is the remote and the laptop is away from its network. Options:

- Move the remote to GitHub or GitLab ([setup.md](setup.md#moving-to-github-or-gitlab)).
- Add `ConnectTimeout=3` for that host in `~/.ssh/config`.

## Hooks do not run on Windows

- `install.py` writes the Python it was run with into each hook. If that Python was removed or moved, run `install.py` again with the current one.
- Open `%USERPROFILE%\.claude\settings.json` and check that the `args` paths exist.
- Run a hook by hand to see errors (the hooks hide them on purpose):
  ```powershell
  '{}' | python $HOME\lumbung\hooks\sync.py
  ```

## No usage from one machine in the report

- That machine has not run a subagent since its last sync, or has not started a session since.
- Its `usage` push failed. On that machine: `git -C ~/lumbung push origin usage`. The error explains why (often credentials).
- The report fetches first. Use `--no-fetch` only when offline.

## Start over on one machine

```bash
python install.py --uninstall
python install.py --host <name>
```

To also reset the usage log, delete `~/.claude/lumbung/usage.jsonl` before reinstalling. Copies already published on the `usage` branch stay there until that machine publishes again.

## Restore the old settings.json

The state before the first install is in `~/.claude/lumbung/settings.json.before-lumbung`. Copy it back only if `--uninstall` left something wrong: it is older than any change made since.
