#!/usr/bin/env python3
"""Check this repository's publishable files, without reading user profiles."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    ".gitignore", "LICENSE", "README.md", "README.en.md", "docs/windows.md", "docs/linux.md",
    "docs/setup.md", "assets/cover.png",
    "examples/sunshine.conf.example", "tools/download_release.py", "tools/check_privacy.py",
    "tests/test_download_release.py",
}
PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_" + r"[A-Za-z0-9]{20,}"),
    re.compile(r"\bgithub_pat_" + r"[A-Za-z0-9_]{20,}"),
    re.compile(r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b"),
    re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/"),
    re.compile(r"https?://[^\s/]+/abandon/[^\s]+"),
]


def main():
    errors = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in {".git", "__pycache__", ".venv", "downloads", "local"} for part in relative.parts):
            continue
        name = relative.as_posix()
        if path.is_symlink():
            errors.append(name + ": symlink is not publishable")
            continue
        if not path.is_file():
            continue
        if name not in ALLOWED:
            errors.append(name + ": unexpected file; review before publishing")
            continue
        if name == "assets/cover.png":
            if not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
                errors.append(name + ": expected PNG image")
            continue
        content = path.read_text(encoding="utf-8")
        for index, pattern in enumerate(PATTERNS):
            if pattern.search(content):
                errors.append(name + ": sensitive pattern " + str(index + 1))
    for error in errors:
        print(error)
    if errors:
        return 1
    print("PASS: publishable file allowlist and sensitive-pattern checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
