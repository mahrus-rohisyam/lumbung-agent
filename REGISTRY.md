# Registry agent & skill

Baca sebelum membuat agent atau skill baru. Hook `guard_agent.py` membaca tabel **Agent** di bawah, jadi formatnya jangan diubah: 4 kolom, nama di kolom pertama, path repo ditulis dalam backtick.

Lokasi:
- **kit**: file di `agents/` atau `skills/` folder ini, dipasang ke semua mesin oleh `install.py`.
- **repo: \`<path>\`**: hanya ada di repo itu (path di VM).
- **plugin: <nama>**: dipasang installer lain, jangan diedit dan jangan disalin ke kit.

Kolom "Untuk apa" ditulis dalam bahasa Inggris, karena dibandingkan dengan deskripsi agent (yang juga berbahasa Inggris) untuk mendeteksi duplikat.

## Agent

| Nama | Untuk apa | Lokasi | Status |
|---|---|---|---|
| security-reviewer | Read-only security review of a finished change: input handling, auth, sessions, authorization, SQL, files, redirects, secrets | kit (juga disalin ke core-backend, core-frontend lewat core-template) | aktif |
| slop-reviewer | Read-only review of a diff for AI slop in code, docs, comments, commit messages, UI copy | kit (juga disalin ke core-backend, core-frontend lewat core-template) | aktif |
| dependency-auditor | Vet a Go module or npm package before adding or bumping a dependency | kit (juga disalin ke core-backend, core-frontend lewat core-template) | aktif |
| marketer | Plan, write and render marketing content per brand: videos, landing loops, social images | repo: `/root/marketing` | aktif, butuh repo marketing |
| codebase-memory | Code knowledge graph verification for a task | plugin: codebase-memory-mcp | aktif |
| codebase-memory-scout | Fast code knowledge graph lookup | plugin: codebase-memory-mcp | aktif |
| codebase-memory-auditor | Bounded code knowledge graph audit | plugin: codebase-memory-mcp | aktif |

## Skill

| Nama | Untuk apa | Lokasi | Status |
|---|---|---|---|
| secure-coding | Secure coding rules (used by security-reviewer) | kit | aktif |
| code-slop | Slop patterns in code (used by slop-reviewer) | kit | aktif |
| no-ai-slop | Slop patterns in prose; upstream petergyang/no-ai-slop (hash in core-template `skills-lock.json`) | kit | aktif |
| dependency-check | Dependency vetting procedure (used by dependency-auditor) | kit | aktif |
| campaign, content-radar, new-brand, refresh, retro | Marketing workflow | repo: `/root/marketing` | aktif |
| codebase-memory | How to use the code knowledge graph | plugin: codebase-memory-mcp | aktif |
| reverse-engineer-anything | Reverse engineering with REA | plugin: rea | aktif |
| (synced) | Skills from the claude.ai account, synced by the account | `~/.claude/skills/synced` | jangan disentuh |
