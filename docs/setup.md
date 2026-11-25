# Setup

## Requirements

- **Claude Code 2.1.275 or later** for the one-line install. Older versions use the two-step install below.
- **Git**, with non-interactive read access to your `lumbung-agent` repository (if hosted privately, see [Access to a private repo](#access-to-a-private-repo)).
- **Python 3.8 or later** on the machine. The guard and the usage log are small Python scripts that the plugin's hooks run; you never run them yourself. The plugin finds whichever of `python3`, `python` or `py -3` works. Without Python, the agents, skills and rules still work, and only the guard and the log stay silent.
- **Windows:** Git for Windows, which includes Git Bash. Claude Code runs plugin hooks through it.

## Install (Claude Code)

If you want to customize `REGISTRY.md` and manage your own shared agents, fork this repository first and replace `<owner>/lumbung-agent` below with your fork.

In a Claude Code session:

```
/plugin install lumbung --marketplace <owner>/lumbung-agent
```

Claude Code adds the `lumbung-agent` marketplace, shows what the plugin adds, and asks for a scope. Choose **Install for you (user scope)** so it works in every project on the machine.

Two-step form, for older versions or from a shell:

```
claude plugin marketplace add <owner>/lumbung-agent
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

## Access to a private repo

If your fork is private, Claude Code clones the marketplace with the git credentials already on the machine and never prompts. Set one of these up once per machine.

**SSH key (Linux / macOS)**

1. `ssh-keygen -t ed25519 -C "<machine name>"`, with no passphrase, or one loaded in `ssh-agent`.
2. Add the public key to your Git host (for example GitHub **Settings → SSH and GPG keys**).
3. `ssh -T git@github.com` must greet you without a prompt. That run also adds the host to `known_hosts`.

With `owner/repo` shorthand, Claude Code tries SSH first and falls back to HTTPS.

**HTTPS with a stored credential (Windows / macOS)**

Git for Windows ships Git Credential Manager (and macOS uses the Keychain helper). Store a credential once by cloning the repo in your terminal and signing in through the browser window it opens:

```powershell
git clone https://github.com/<owner>/lumbung-agent $HOME\lumbung-agent
```

The clone is also what you use to develop agents ([workflow.md](workflow.md)). If the machine has no GitHub SSH key, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` in the user environment variables so Claude Code goes straight to HTTPS. Without it, installs from `/plugin` and updates do not fall back on their own.

The alternative is `gh auth login`, then `gh auth setup-git`.

A `GITHUB_TOKEN` environment variable alone does not work: Claude Code uses git's credential helpers, not tokens.

## Local-path install (offline or single machine)

If a machine does not have remote Git access yet, you can add a local clone as the marketplace:

```bash
claude plugin marketplace add /path/to/lumbung-agent
claude plugin install lumbung@lumbung-agent
```

Added from a local path, the plugin loads **in place**: Claude Code runs whatever branch is currently checked out in that clone at every session start.

To move from a local path to a Git remote later:

```bash
claude plugin marketplace remove lumbung-agent
claude plugin install lumbung --marketplace <owner>/lumbung-agent
```

Removing the marketplace uninstalls the plugin. The usage log in `~/.claude/plugins/data/lumbung-lumbung-agent/` survives only if you copy it aside first, because uninstalling deletes the plugin's data folder.

## Remove

`/plugin` → **Installed** → `lumbung` → **Uninstall**, or `claude plugin uninstall lumbung@lumbung-agent`. Add `--keep-data` to keep the usage log.

## Install (Antigravity)

Lumbung ships a native Antigravity plugin layout (`plugin.json`, `hooks.json`, `rules/AGENTS.md`, `skills/`, and `agents/`).

### Global install (recommended, works in every workspace)

Run once per machine:

```bash
# Linux / macOS
git clone https://github.com/<owner>/lumbung-agent ~/.gemini/config/plugins/lumbung
```

```powershell
# Windows (PowerShell)
git clone https://github.com/<owner>/lumbung-agent $HOME\.gemini\config\plugins\lumbung
```

If you already cloned `lumbung-agent` elsewhere for development, symlink it instead:

```bash
ln -s /path/to/lumbung-agent ~/.gemini/config/plugins/lumbung
```

### Workspace install (single project only)

```bash
git clone https://github.com/<owner>/lumbung-agent .agents/plugins/lumbung
```

### Update & check it

- **Update:** `git -C ~/.gemini/config/plugins/lumbung pull`
- **Check it:** Open **Customizations** in Antigravity to see **Lumbung** enabled, or ask the agent to use a skill (e.g. `Use $marketing` or `Use $seo-audit`). Skills, `rules/AGENTS.md`, and the duplicate-agent `PreToolUse` guard (`hooks.json`) activate automatically on the next turn without restarting.
- **Remove:** Delete `~/.gemini/config/plugins/lumbung` (or `.agents/plugins/lumbung`) or disable it from **Customizations**.

## Coexisting with other plugins

Lumbung never modifies agents, skills, or hooks installed by other plugins. List third-party plugins in `REGISTRY.md` with `plugin: <name>` so the duplicate guard and other sessions know they exist.
