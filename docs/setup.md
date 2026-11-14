# Setup

## Requirements

- Claude Code on the machine.
- Python 3.8 or later. Lumbung uses the standard library only; nothing to `pip install`.
- Git, and passwordless access to the `origin` remote (SSH key or a credential helper). Hooks run without a terminal, so git can never ask for a password; if it would, sync silently does nothing.

## 1. Choose the remote

All machines sync through the `origin` remote of their clone. Two setups work; the code is the same for both.

| Remote | Works when | Notes |
|---|---|---|
| **The VM** (`root@<vm>:/root/lumbung`) | The machine can SSH to the VM | No third party. Syncing stops when the VM is down or unreachable. The VM's own checkout has no `origin`. |
| **Private GitHub or GitLab repo** | The machine has internet | Works without the VM. Every machine, the VM included, clones from it. Gives an off-machine backup. |

The repo must be **private**: the registry contains local paths and machine names, and usage logs contain working-directory paths.

### VM as the remote (current setup)

The VM repo accepts pushes to its checked-out branch:

```bash
git -C /root/lumbung config receive.denyCurrentBranch updateInstead
```

Clients use `root@<vm>:/root/lumbung` as `origin`. `<vm>` is whatever host or SSH alias you already use to reach the VM.

### Moving to GitHub or GitLab

1. Create an empty private repo (no README, no license).
2. Give every machine access. One SSH key per machine, added to your account, is the simplest; Git Credential Manager on Windows also works with HTTPS.
3. On the VM:
   ```bash
   cd /root/lumbung
   git remote add origin <url>
   git push -u origin master
   git push origin usage          # if the usage branch exists
   ```
4. On each Windows machine that cloned from the VM:
   ```powershell
   git -C $HOME\lumbung remote set-url origin <url>
   git -C $HOME\lumbung fetch origin
   ```
5. Optional: set `receive.denyCurrentBranch` back to the default on the VM, since nobody pushes to it any more.

## 2. Install on the VM

```bash
python3 /root/lumbung/install.py --host vm
```

## 3. Install on the laptop and PC (PowerShell)

```powershell
git clone <origin-url> $HOME\lumbung
python $HOME\lumbung\install.py --host laptop     # on the PC: --host pc
```

Check it:

```powershell
git -C $HOME\lumbung fetch origin     # must finish without a password prompt
claude                                # new session; /agents should list the kit's agents
```

`--host` is the name in usage logs. Use one short, stable name per machine; it becomes the file name `usage/<host>.jsonl`. Without it, the machine's hostname is used.

## What install.py changes

Everything lives under `~/.claude` (`%USERPROFILE%\.claude` on Windows):

| Path | Change |
|---|---|
| `agents/<name>.md` | Kit agents copied in. Only names in Lumbung's manifest are ever replaced or removed. |
| `skills/<name>/` | Kit skills copied in, same rule. |
| `CLAUDE.md` | The block from `rules/CLAUDE.md` between `<!-- BEGIN lumbung -->` and `<!-- END lumbung -->`. Text outside the block is kept. |
| `settings.json` | Four hook entries whose script path points into this repo. Other hooks and settings are kept. The first install saves a copy as `lumbung/settings.json.before-lumbung`. |
| `lumbung/` | `config.json` (host name, installed commit), `manifest.json`, `usage.jsonl`. |

Running it again is safe: it removes its own entries first and adds them back.

If an agent or skill with the same name already exists and did not come from Lumbung, install prints a warning and replaces it. Check the warning: that file was probably an older hand-made copy.

## Uninstall

```bash
python3 install.py --uninstall
```

Removes the kit's agents and skills, the CLAUDE.md block and the hook entries. The usage log and the settings backup in `~/.claude/lumbung/` are kept; delete that folder by hand if you want them gone.

## Related setups

- **core-template**: its `.claude/agents/{security-reviewer,slop-reviewer,dependency-auditor}.md` and `.agents/skills/{secure-coding,code-slop,no-ai-slop,dependency-check}` are symlinks into `/root/lumbung`. `sync-agent-kit.py` follows the links and writes real files into `core-backend` and `core-frontend`, so those public repos stay self-contained. Text in these shared agents and skills must stay free of personal setup details, because it ends up in public repos.
- **codebase-memory-mcp** installs its own agents, skills and hooks into `~/.claude`. Lumbung never touches them.
