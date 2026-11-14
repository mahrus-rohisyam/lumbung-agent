# Troubleshooting

## A new agent from another machine does not show up

1. **Was it pushed to `master`?** On the machine that made it: `git log origin/master -1`.
2. **Is auto-update on?** `/plugin` → **Marketplaces** → `lumbung-agent`. If it says **Enable auto-update**, it is off.
3. **Auto-update is not instant.** It runs in the background after your first message of a session, within about ten minutes, and the new version loads in the next session (or after `/reload-plugins`). To update right away: **Update marketplace** on the same screen, then `/reload-plugins`.
4. **Can this machine reach the repo without a prompt?** From a shell: `git ls-remote https://github.com/mahrus-rohisyam/lumbung-agent` (or the SSH form). If it asks for anything, fix access first ([setup.md](setup.md#access-to-the-private-repo)). Background updates fail quietly and keep the old version.
5. `claude plugin list` shows the installed version (a commit SHA). Compare it with `git rev-parse --short=12 origin/master` in a clone.

## Install fails with an authentication or "repository not found" error

The repo is private and Claude Code never prompts. Set up an SSH key or a stored HTTPS credential ([setup.md](setup.md#access-to-the-private-repo)). On Windows without a GitHub SSH key, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`.

## The guard blocked an agent that is not a duplicate

Read the message: it names the matching agent and the shared terms.

- If the other agent really covers it, extend that one instead.
- If the match is wrong, make the new description more specific. Generic words like "review" or "change" add up quickly.
- If it is a real, intended second version, add `# lumbung-override: <reason>` to the frontmatter and a registry row.

If it misfires often, raise `THRESHOLD` or `MIN_SHARED` in `hooks/guard_agent.py`, or add the noisy word to `STOP`.

## "is a plugin copy managed by Claude Code"

You, or Claude, tried to edit a file under `~/.claude/plugins/`. Edit the same file in your clone on a feature branch instead ([workflow.md](workflow.md)).

## The guard or the usage log does nothing on Windows

- Python must be installed and runnable as `python`, `python3` or `py -3` from Git Bash. Check in Git Bash: `python --version`, `py -3 --version`.
- If `python3` opens the Microsoft Store, that is the stub. `run.sh` skips it, but turning it off in **Settings → Apps → Advanced app settings → App execution aliases** avoids the confusion.
- Run a hook by hand to see errors (hooks hide them on purpose). In Git Bash, from a clone:
  ```bash
  echo '{"hook_event_name":"SubagentStart","agent_type":"test"}' | sh hooks/run.sh hooks/log_usage.py
  ```
  Then check `~/.claude/plugins/data/lumbung-lumbung-agent/usage.jsonl`.
- `/plugin` → **Errors** shows plugin load problems.

## `/lumbung:report` shows nothing

No subagent has run on this machine since the plugin was installed, or the log was deleted with an uninstall. Built-in agents count too, so any `Explore` or `Plan` run should appear.

## `--plugin-dir` session still shows the old agent

The clone replaces the installed plugin only when its manifest name is `lumbung`, which it is unless you changed `plugin.json`. Check that you started `claude` with the right path, and run `/reload-plugins` after edits.

## The VM runs a feature branch everywhere

While the VM installs from the local path, the plugin loads in place from `/root/lumbung-agent`, so every session there runs the checked-out branch. `git switch master` puts it back. Installing from GitHub on the VM removes this effect ([setup.md](setup.md#machines)).
