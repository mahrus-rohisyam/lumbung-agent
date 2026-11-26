#!/usr/bin/env python3
"""Detect and remove invisible Unicode watermarks, bidi controls, and sneaky spaces.

Standard library only. Defaults to check mode (exit 1 when findings exist).
Use --fix to rewrite affected files in place.
"""

import argparse
import os
import subprocess
import sys
import unicodedata
from pathlib import Path

# Invisible / watermark / Trojan Source characters removed outright.
STRIP_CODEPOINTS = {
    0x00AD,  # SOFT HYPHEN
    0x034F,  # COMBINING GRAPHEME JOINER
    0x061C,  # ARABIC LETTER MARK
    0x180E,  # MONGOLIAN VOWEL SEPARATOR
    0x200B,  # ZERO WIDTH SPACE
    0x200C,  # ZERO WIDTH NON-JOINER
    0x200D,  # ZERO WIDTH JOINER
    0x200E,  # LEFT-TO-RIGHT MARK
    0x200F,  # RIGHT-TO-LEFT MARK
    0x202A,  # LEFT-TO-RIGHT EMBEDDING
    0x202B,  # RIGHT-TO-LEFT EMBEDDING
    0x202C,  # POP DIRECTIONAL FORMATTING
    0x202D,  # LEFT-TO-RIGHT OVERRIDE
    0x202E,  # RIGHT-TO-LEFT OVERRIDE
    0x2060,  # WORD JOINER
    0x2061,  # FUNCTION APPLICATION
    0x2062,  # INVISIBLE TIMES
    0x2063,  # INVISIBLE SEPARATOR
    0x2064,  # INVISIBLE PLUS
    0x2066,  # LEFT-TO-RIGHT ISOLATE
    0x2067,  # RIGHT-TO-LEFT ISOLATE
    0x2068,  # FIRST STRONG ISOLATE
    0x2069,  # POP DIRECTIONAL ISOLATE
    0xFEFF,  # ZERO WIDTH NO-BREAK SPACE / stray BOM (allowed only at index 0)
}

# Non-standard whitespace normalized to plain ASCII whitespace.
SPACE_REPLACEMENTS = {
    0x00A0: " ",   # NO-BREAK SPACE
    0x2000: " ",   # EN QUAD
    0x2001: " ",   # EM QUAD
    0x2002: " ",   # EN SPACE
    0x2003: " ",   # EM SPACE
    0x2004: " ",   # THREE-PER-EM SPACE
    0x2005: " ",   # FOUR-PER-EM SPACE
    0x2006: " ",   # SIX-PER-EM SPACE
    0x2007: " ",   # FIGURE SPACE
    0x2008: " ",   # PUNCTUATION SPACE
    0x2009: " ",   # THIN SPACE
    0x200A: " ",   # HAIR SPACE
    0x2028: "\n",  # LINE SEPARATOR
    0x2029: "\n",  # PARAGRAPH SEPARATOR
    0x202F: " ",   # NARROW NO-BREAK SPACE (common LLM watermark)
    0x205F: " ",   # MEDIUM MATHEMATICAL SPACE
    0x3000: " ",   # IDEOGRAPHIC SPACE
}

# Optional typographic normalization (--ascii-punct).
ASCII_PUNCT_REPLACEMENTS = {
    0x2018: "'",   # LEFT SINGLE QUOTATION MARK
    0x2019: "'",   # RIGHT SINGLE QUOTATION MARK
    0x201C: '"',   # LEFT DOUBLE QUOTATION MARK
    0x201D: '"',   # RIGHT DOUBLE QUOTATION MARK
    0x2010: "-",   # HYPHEN
    0x2011: "-",   # NON-BREAKING HYPHEN
    0x2012: "-",   # FIGURE DASH
    0x2013: "-",   # EN DASH
    0x2014: "--",  # EM DASH
    0x2026: "...", # HORIZONTAL ELLIPSIS
    0x2212: "-",   # MINUS SIGN
}

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next"}


def is_tag_or_vs_smuggling(cp):
    # Unicode Tags (U+E0000..U+E007F) and Variation Selectors Supplement (U+E0100..U+E01EF)
    # are frequently abused for invisible watermarks and prompt smuggling.
    return (0xE0000 <= cp <= 0xE007F) or (0xE0100 <= cp <= 0xE01EF)


def replacement_for(ch, idx, ascii_punct):
    cp = ord(ch)
    if cp == 0xFEFF and idx == 0:
        return None
    if cp in STRIP_CODEPOINTS or is_tag_or_vs_smuggling(cp):
        return ""
    if cp in SPACE_REPLACEMENTS:
        return SPACE_REPLACEMENTS[cp]
    if ascii_punct and cp in ASCII_PUNCT_REPLACEMENTS:
        return ASCII_PUNCT_REPLACEMENTS[cp]
    return None


def char_label(ch):
    cp = ord(ch)
    name = unicodedata.name(ch, "UNKNOWN")
    return f"U+{cp:04X} {name}"


def is_binary(raw):
    return b"\x00" in raw[:8192]


def process_file(path, fix=False, ascii_punct=False):
    try:
        raw = path.read_bytes()
    except OSError as exc:
        print(f"warn: cannot read {path}: {exc}", file=sys.stderr)
        return []
    if is_binary(raw):
        return []
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return []

    findings = []
    out_chars = []
    line, col = 1, 1
    changed = False

    for idx, ch in enumerate(text):
        rep = replacement_for(ch, idx, ascii_punct)
        if rep is not None:
            action = "remove" if rep == "" else f"replace with {rep!r}"
            findings.append((path, line, col, char_label(ch), action))
            out_chars.append(rep)
            changed = True
        else:
            out_chars.append(ch)
        if ch == "\n":
            line += 1
            col = 1
        else:
            col += 1

    if fix and changed:
        path.write_text("".join(out_chars), encoding="utf-8")
    return findings


def git_changed_files(staged=False, base=None):
    top = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    if top.returncode != 0:
        print(f"error: not a git repository: {top.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    root = Path(top.stdout.strip())

    if staged:
        cmd = ["git", "-c", "core.quotepath=false", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    elif base:
        cmd = ["git", "-c", "core.quotepath=false", "diff", f"{base}...HEAD", "--name-only", "--diff-filter=ACMR"]
    else:
        cmd = ["git", "-c", "core.quotepath=false", "diff", "--name-only", "--diff-filter=ACMR"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"error: git diff failed: {proc.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    files = [root / line for line in proc.stdout.splitlines() if line.strip()]
    if not staged and not base:
        # Include untracked and staged files when checking working tree.
        extra = subprocess.run(
            ["git", "-c", "core.quotepath=false", "status", "--porcelain"],
            capture_output=True, text=True,
        )
        if extra.returncode == 0:
            for row in extra.stdout.splitlines():
                if len(row) > 3 and row[0] != "D" and row[1] != "D":
                    p = row[3:].split(" -> ")[-1].strip().strip('"')
                    if p:
                        files.append(root / p)
    seen, unique = set(), []
    for f in files:
        if f.is_file() and f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def iter_paths(targets):
    for raw in targets:
        p = Path(raw)
        if p.is_file():
            yield p
        elif p.is_dir():
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for name in sorted(files):
                    yield Path(root) / name


def main():
    parser = argparse.ArgumentParser(
        description="Detect or remove invisible Unicode watermarks, bidi controls, and non-ASCII spaces."
    )
    parser.add_argument("paths", nargs="*", help="Files or directories to scan.")
    parser.add_argument("--diff", nargs="?", const="", default=None, metavar="BASE",
                        help="Scan git changed files (working tree by default, or BASE...HEAD).")
    parser.add_argument("--staged", action="store_true", help="Scan staged git files.")
    parser.add_argument("--fix", action="store_true", help="Rewrite files in place.")
    parser.add_argument("--ascii-punct", action="store_true",
                        help="Also normalize smart quotes, non-breaking hyphens, and dashes to ASCII.")
    args = parser.parse_args()

    if args.staged:
        files = git_changed_files(staged=True)
    elif args.diff is not None:
        files = git_changed_files(base=args.diff or None)
    elif args.paths:
        files = list(iter_paths(args.paths))
    else:
        parser.error("Provide paths, --diff, or --staged.")

    all_findings = []
    for path in files:
        all_findings.extend(process_file(path, fix=args.fix, ascii_punct=args.ascii_punct))

    for path, line, col, label, action in all_findings:
        prefix = "fixed" if args.fix else "found"
        print(f"{path}:{line}:{col}: [{prefix}] {label} ({action})")

    if not all_findings:
        print(f"clean ({len(files)} files checked)")
        return 0
    if args.fix:
        print(f"fixed {len(all_findings)} issue(s) across {len({f[0] for f in all_findings})} file(s)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
