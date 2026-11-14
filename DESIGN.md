# Rancangan agent-harness

## 1. Struktur repo

```
agent-harness/
├── README.md
├── DESIGN.md
├── REGISTRY.md              # daftar agent & skill (diisi manual, dicek oleh hook)
├── agents/                  # agent level user → ~/.claude/agents/
├── skills/                  # skill level user  → ~/.claude/skills/
├── rules/CLAUDE.md          # blok aturan → digabung ke ~/.claude/CLAUDE.md
├── hooks/
│   ├── sync.py              # SessionStart: git pull + install + kirim log
│   ├── guard_agent.py       # PreToolUse Write|Edit: cek agent baru vs registry
│   └── log_usage.py         # SubagentStart/SubagentStop: catat pemakaian
├── install.py               # pasang ke ~/.claude di mesin mana pun (Linux/Windows)
└── report.py                # di VM: rangkum log gabungan
```

Semua script Python (stdlib saja), supaya sama di Linux dan Windows.

## 2. Apa yang masuk kit, apa yang tidak

| Jenis | Masuk kit? | Alasan |
|---|---|---|
| Agent umum (berguna di banyak repo), mis. security-reviewer, slop-reviewer, dependency-auditor | Ya, ke `agents/` | Ini yang dicari di mesin lain |
| Agent terikat repo, mis. `marketer` (butuh file & Remotion di `/root/marketing`) | Tidak. Tetap di repo, **dicatat di registry** | Tanpa repo-nya agent ini tidak berguna |
| Agent dari plugin/installer, mis. `codebase-memory*` di `~/.claude/agents` | Tidak, hanya dicatat | Dikelola installer `codebase-memory-mcp`; ditimpa saat update |
| `~/.claude/skills/synced/` | Tidak disentuh | Skill dari akun claude.ai, sudah sinkron sendiri lewat akun |
| Hook `codebase-memory-mcp` di settings.json | Tidak disentuh | `install.py` hanya menambah entri miliknya sendiri |

Kalau agent terikat repo ternyata ada bagian yang berguna umum (mis. menulis report dari marketer), bagian itu dipisah jadi agent level user.

### Hubungan dengan core-template

`core-template` tetap sumber kit untuk repo publik (`core-backend`, `core-frontend`) karena repo publik harus berdiri sendiri. Agar tidak ditulis dua kali, agent yang sama (security-reviewer, slop-reviewer, dependency-auditor) punya **satu** sumber. Pilihan:

- A. Sumber di `agent-harness/agents/`, `sync-agent-kit.py` menyalin dari sini.
- B. Sumber tetap di `core-template`, `install.py` menyalin dari sana di VM.

Usul: **A**, karena agent-harness yang di-clone ke semua mesin. Catatan: agent itu merujuk skill (`secure-coding`, `code-slop`, `no-ai-slop`, `dependency-check`), jadi skill-nya ikut pindah ke `skills/`. Teks agent harus tetap bebas detail setup pribadi karena ikut ke repo publik.

## 3. Sinkron antar mesin

**Pemasangan awal (laptop/komputer, PowerShell):**

```
git clone ssh://<vm>/root/agent-harness $HOME\agent-harness
python $HOME\agent-harness\install.py
```

**`install.py`:**

- Menyalin `agents/*` dan `skills/*` ke `~/.claude/` (Windows: `%USERPROFILE%\.claude\`). Hanya file yang tercatat sebagai milik kit (manifest) yang ditimpa/dihapus; file lain dibiarkan.
- Menggabungkan blok `rules/CLAUDE.md` ke `~/.claude/CLAUDE.md` di antara penanda `<!-- BEGIN agent-harness -->` / `<!-- END agent-harness -->`.
- Menambah hook ke `~/.claude/settings.json` tanpa mengubah hook lain. Path script ditulis sesuai OS.
- Idempoten: dijalankan berkali-kali hasilnya sama.

**Sinkron otomatis (`hooks/sync.py`, SessionStart):**

1. `git pull --ff-only` dengan timeout ±3 detik. Gagal (offline/VM mati) → diam, lanjut kerja.
2. Kalau ada perubahan → jalankan `install.py`.
3. Kirim log pemakaian yang belum terkirim ke VM (lihat bagian 5).

Agent baru yang di-commit di VM tersedia di laptop pada sesi berikutnya. Agent yang ada saat sesi berjalan tidak berubah sampai sesi baru (perilaku Claude Code saat memuat agent; perlu dicek).

**Di VM sendiri:** kit di-install dari folder ini langsung; hook sync cukup menjalankan install kalau ada commit baru.

**Membuat/mengubah agent dari laptop/komputer:** edit di clone `agent-harness`, commit, `git push` ke VM. VM menyimpan repo dengan working tree, jadi push ke branch yang sedang di-checkout perlu `receive.denyCurrentBranch=updateInstead` di VM (atau pakai bare repo terpisah; lihat pertanyaan terbuka).

## 4. Mencegah agent dobel

Tiga lapis:

1. **Registry** (`REGISTRY.md`): nama, ringkasan, lokasi (kit / repo X / plugin), status.
2. **Aturan** di `rules/CLAUDE.md`: sebelum membuat agent, baca registry. Kalau ada yang mirip, pakai atau perluas yang ada. Agent umum dibuat di agent-harness, bukan di repo yang sedang dibuka. Agent baru wajib ditambah ke registry di commit yang sama.
3. **Hook pagar** (`hooks/guard_agent.py`, PreToolUse `Write|Edit`):
   - Hanya aktif kalau path cocok `*/.claude/agents/*.md`.
   - Ambil `name` dan `description` dari frontmatter yang akan ditulis.
   - Bandingkan dengan registry: nama sama, atau deskripsi mirip (overlap kata kunci, ambang ditentukan saat implementasi).
   - Mirip → blok dengan pesan: "agent X di <lokasi> sudah melakukan ini; pakai atau perluas". Bisa dilewati dengan alasan eksplisit (mis. versi khusus repo), yang lalu dicatat di registry.
   - Nama tidak ada di registry → izinkan, tapi ingatkan untuk menambah ke registry.

Catatan: agent di repo menang atas agent level user dengan nama sama. Itu boleh untuk versi khusus, asal tercatat di registry.

## 5. Monitoring pemakaian

**Pencatatan (`hooks/log_usage.py`):** di event `SubagentStart` dan `SubagentStop` (keduanya ada di Claude Code 2.1.319 terpasang; isi payload dicek saat implementasi). Satu baris JSON per event ke `~/.claude/agent-harness/usage.jsonl`:

```json
{"ts":"2026-11-14T09:12:03Z","host":"laptop","event":"start","agent":"slop-reviewer","cwd":"C:\\work\\report","session":"..."}
```

**Pengiriman ke VM:** di `sync.py`, baris yang belum terkirim di-append ke VM lewat SSH:
`ssh <vm> "cat >> /root/.claude/agent-harness/usage-all.jsonl"`, lalu offset lokal disimpan. Gagal → dicoba lagi di sesi berikutnya. Di VM log langsung ditulis ke file gabungan.

**Rangkuman (`report.py`, di VM):**

- Pemakaian per agent, per mesin, per repo, per minggu.
- Agent di registry yang tidak pernah dipakai dalam N hari → kandidat dihapus.
- Agent terikat repo yang dipakai di banyak repo → kandidat dipindah ke kit.

Tidak perlu dashboard dulu. Kalau nanti perlu, bisa jadi halaman sederhana dari `report.py`.

## 6. Catatan Windows

- Path `~/.claude` = `%USERPROFILE%\.claude`.
- Perintah hook memanggil `python <path>\hooks\x.py`; `install.py` menulis path absolut per mesin.
- Cara Claude Code di Windows menjalankan command hook (cmd/PowerShell/Git Bash) dicek saat implementasi, supaya quoting path benar.
- SSH memakai OpenSSH bawaan Windows dan key yang sudah ada.
- Line ending: `.gitattributes` dengan `* text=auto eol=lf` supaya frontmatter agent tidak rusak.

## 7. Pertanyaan terbuka

1. Repo VM: working tree + `updateInstead`, atau bare repo terpisah (`/root/agent-harness.git`) dan VM juga clone dari sana? Usul: `updateInstead`, lebih sederhana untuk satu orang.
2. Sumber agent umum: agent-harness (A) atau core-template (B)? Usul: A.
3. Hook pagar: blok keras atau hanya peringatan? Usul: blok, bisa dilewati dengan alasan.
4. Apakah MCP server (mis. openproject, codebase-memory) ikut dikelola kit? Usul: tidak dulu. Sebagian adalah binary/kredensial per mesin; cukup dicatat di registry.
5. Backup offsite repo (GitLab privat)? Opsional, kalau VM rusak (lihat riwayat masalah disk sdb).

## Rencana implementasi

1. `git init` di folder ini, `.gitattributes`, isi `REGISTRY.md` final.
2. Pindahkan agent & skill umum ke `agents/` dan `skills/` (opsi A), arahkan `sync-agent-kit.py` ke sini.
3. `install.py` + `rules/CLAUDE.md`; pasang di VM, cek settings.json lama tetap utuh.
4. `guard_agent.py`; uji: buat agent dobel → diblokir, agent baru → lolos + pengingat.
5. `log_usage.py` + `report.py`; uji dengan satu subagent.
6. `sync.py`; clone & install di komputer, lalu laptop; uji agent baru di VM muncul di sesi baru Windows.
