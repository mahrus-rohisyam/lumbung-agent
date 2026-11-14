# agent-harness

Satu sumber untuk agent, skill, aturan, dan hook Claude Code yang dipakai di semua mesin: VM (pusat), laptop, dan komputer.

Status (2026-11-14): **terpasang di VM**. Laptop dan komputer belum. Rancangan dan pertanyaan terbuka ada di [DESIGN.md](DESIGN.md).

## Pemasangan

**VM (sudah):** `python3 /root/agent-harness/install.py --host vm`

**Laptop / komputer (PowerShell):**

```powershell
git clone root@<vm>:/root/agent-harness $HOME\agent-harness
python $HOME\agent-harness\install.py --hub root@<vm> --host laptop   # atau --host komputer
```

`<vm>` = host atau alias SSH yang biasa dipakai untuk konek ke VM (harus bisa tanpa password). Setelah itu sinkron jalan sendiri tiap sesi Claude Code dimulai.

**Membatalkan:** `python install.py --uninstall` (settings lama juga dibackup di `~/.claude/agent-harness/settings.json.before-agent-harness`).

## Pemakaian sehari-hari

- Ubah atau tambah agent/skill umum di `agents/` atau `skills/`, perbarui `REGISTRY.md`, commit. Di laptop/komputer: `git push` juga. Mesin lain mengambilnya di sesi berikutnya.
- Lihat pemakaian (di VM): `python3 /root/agent-harness/report.py --days 30`.
- `core-template` memakai agent dan skill ini lewat symlink, jadi `sync-agent-kit.py` menyalin versi kit ke repo core.

## Masalah

1. Agent yang bagus ada di VM, tapi tidak ada di laptop/komputer saat sedang kerja di sana (dan sebaliknya).
2. Repo baru cenderung membuat agent baru sendiri, padahal fungsinya sudah ada di repo lain → redundant.
3. Tidak ada catatan agent mana yang benar-benar dipakai, di mesin mana, di repo mana.

## Mesin

| Mesin | OS | Dipakai untuk | Akses ke VM |
|---|---|---|---|
| VM | Linux | Develop utama (laptop & komputer biasanya konek ke sini) | — |
| Laptop | Windows | Report, marketing; saat resource VM kurang | SSH (key) |
| Komputer | Windows | Develop aplikasi Windows; saat resource VM kurang | SSH (key) |

Python sudah terpasang di ketiganya.

## Ide inti

- **VM = sumber kebenaran.** Folder ini (`/root/agent-harness`) jadi repo git. Laptop & komputer `git clone` lewat SSH dari VM, tanpa GitHub/GitLab.
- **Sinkron otomatis** lewat hook `SessionStart`: `git pull` + `install.py`, timeout pendek, diam kalau VM tidak terjangkau.
- **Registry** ([REGISTRY.md](REGISTRY.md)) mendaftar semua agent & skill, di mana tinggalnya, dan untuk apa.
- **Hook pagar**: setiap penulisan `*/.claude/agents/*.md` dicek ke registry; yang mirip diperingatkan/diblokir.
- **Log pemakaian** per mesin (dengan nama mesin), dikirim ke VM, dirangkum di VM.

Detail: [DESIGN.md](DESIGN.md).
