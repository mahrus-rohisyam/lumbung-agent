# Setup

## Requirements

- **Claude Code 2.1.275 or later** for the one-line install. Older versions use the two-step install below.
- **Git**, with read access to the private repo `mahrus-rohisyam/lumbung-agent` that works without a prompt. See [Access to the private repo](#access-to-the-private-repo).
- **Python 3.8 or later** on the machine. The guard and the usage log are small Python scripts that the plugin's hooks run; you never run them yourself. The plugin finds whichever of `python3`, `python` or `py -3` works. Without Python, the agents, skills and rules still work, and only the guard and the log stay silent.
- **Windows:** Git for Windows, which includes Git Bash. Claude Code runs plugin hooks through it.

## Install

In a Claude Code session:

```
/plugin install lumbung --marketplace mahrus-rohisyam/lumbung-agent
```

Claude Code adds the `lumbung-agent` marketplace, shows what the plugin adds, and asks for a scope. Choose **Install for you (user scope)** so it works in every project on the machine.

Two-step form, for older versions or from a shell:

```
claude plugin marketplace add mahrus-rohisyam/lumbung-agent
claude plugin install lumbung@lumbung-agent
```

### Turn on auto-update

Auto-update is off by default for any marketplace that is not Anthropic's. Turn it on once per machine: `/plugin` → **Marketplaces** → `lumbung-agent` → **Enable auto-update**.

With it on, Claude Code checks for new commits in the background shortly after a session starts (after your first message, within about ten minutes). It downloads the update and says `Plugin updated: lumbung · Run /reload-plugins to apply`. The next session uses the new version either way.

There is no `version` in `plugin.json` on purpose: Claude Code then tracks commits, so every push to `master` is a release.

### Check it

```
/agents                  # lists lumbung:security-reviewer and the others
/lumbung:report          # prints the usage summary (empty at first)
```

Or from a shell: `claude plugin list` shows `lumbung@lumbung-agent` with `Status: ✔ enabled`.

## Access to the private repo

Claude Code clones the marketplace with the git credentials already on the machine and never prompts. Set one of these up once per machine.

**SSH key (simplest on the VM)**

1. `ssh-keygen -t ed25519 -C "<machine name>"`, with no passphrase, or one loaded in `ssh-agent`.
2. Add the public key to GitHub: **Settings → SSH and GPG keys**.
3. `ssh -T git@github.com` must greet you without a prompt. That run also adds github.com to `known_hosts`.

With `owner/repo` shorthand, Claude Code tries SSH first and falls back to HTTPS.

**HTTPS with a stored credential (simplest on Windows)**

Git for Windows ships Git Credential Manager. Store a credential once by cloning the repo in PowerShell and signing in through the browser window it opens:

```powershell
git clone https://github.com/mahrus-rohisyam/lumbung-agent $HOME\lumbung-agent
```

The clone is also what you use to develop agents ([workflow.md](workflow.md)). If the machine has no GitHub SSH key, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` in the user environment variables so Claude Code goes straight to HTTPS. Without it, installs from `/plugin` and updates do not fall back on their own.

The alternative is `gh auth login`, then `gh auth setup-git`.

A `GITHUB_TOKEN` environment variable alone does not work: Claude Code uses git's credential helpers, not tokens.

## Machines

| Machine | Install from | Notes |
|---|---|---|
| VM | GitHub, once the VM has an SSH key. Until then, from the local clone: `claude plugin marketplace add /root/lumbung-agent` | Added from a local path, the plugin loads in place: the VM runs whatever is checked out in `/root/lumbung-agent`, at every session start |
| Laptop | GitHub | HTTPS with Git Credential Manager |
| PC | GitHub | HTTPS with Git Credential Manager |

To move the VM from the local path to GitHub:

```
claude plugin marketplace remove lumbung-agent
claude plugin install lumbung --marketplace mahrus-rohisyam/lumbung-agent
```

Removing the marketplace uninstalls the plugin. The usage log in `~/.claude/plugins/data/lumbung-lumbung-agent/` survives only if you copy it aside first, because uninstalling deletes the plugin's data folder.

## Remove

`/plugin` → **Installed** → `lumbung` → **Uninstall**, or `claude plugin uninstall lumbung@lumbung-agent`. Add `--keep-data` to keep the usage log.

## Related setups

- **core-template**: `.claude/agents/{security-reviewer,slop-reviewer,dependency-auditor}.md` and `.agents/skills/{secure-coding,code-slop,no-ai-slop,dependency-check}` are symlinks into `/root/lumbung-agent`. `sync-agent-kit.py` follows the links and writes real files into `core-backend` and `core-frontend`, so those public repos stay self-contained. Keep the text of these shared files free of personal setup details, because it ends up in public repos. Inside those repos the agents also exist without the `lumbung:` prefix; that is expected.
- **codebase-memory-mcp** installs its own agents, skills and hooks into `~/.claude`. Lumbung never touches them.
