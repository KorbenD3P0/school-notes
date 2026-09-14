#!/usr/bin/env python3
"""Import notes from the Obsidian vault into this repo, converting Obsidian's
wikilink syntax to plain markdown GitHub can actually render.

Usage:
    python3 scripts/import_from_obsidian.py <vault-subpath> <course-slug>

Example:
    python3 scripts/import_from_obsidian.py "College/Physics" phy1000

<vault-subpath> is relative to the vault root (below). It can be a single
.md file or a folder (imported recursively). <course-slug> is the folder
name under courses/ to import into (created if it doesn't exist).

What it converts:
    ![[image.png]]          -> ![](images/image.png)   (and copies the file,
    ![[image.png|300]]         searched for vault-wide by filename, into
                                courses/<slug>/images/)
    [[Some Note]]           -> [Some Note](Some%20Note.md)   (a same-folder
    [[Some Note|shown]]     -> [shown](Some%20Note.md)         relative link;
                                best-effort, doesn't verify the target exists)

Safe to rerun -- re-importing overwrites the previously imported copies of
the same files, so this doubles as a "resync this note" command.
"""
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

VAULT_ROOT = Path.home() / "storage/shared/Documents/Obsidian/DPU (Remote)"
REPO_ROOT = Path(__file__).parent.parent

EMBED_RE = re.compile(r"!\[\[([^\]|]+?)(?:\|[^\]]*)?\]\]")
LINK_RE = re.compile(r"(?<!!)\[\[([^\]|]+?)(?:\|([^\]]+))?\]\]")


def find_in_vault(filename):
    """Vault-wide search by filename (Obsidian attachments can live anywhere)."""
    matches = list(VAULT_ROOT.rglob(filename))
    return matches[0] if matches else None


def convert_note(text, images_dir):
    copied = []
    missing = []

    def embed_sub(m):
        fname = m.group(1).strip()
        src = find_in_vault(fname)
        if src is None:
            missing.append(fname)
            return m.group(0)  # leave untouched so it's easy to grep for later
        dest = images_dir / src.name
        images_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied.append(src.name)
        return f"![]({urllib.parse.quote('images/' + src.name)})"

    def link_sub(m):
        target, display = m.group(1).strip(), m.group(2)
        label = display.strip() if display else target
        return f"[{label}]({urllib.parse.quote(target)}.md)"

    text = EMBED_RE.sub(embed_sub, text)
    text = LINK_RE.sub(link_sub, text)
    return text, copied, missing


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    vault_subpath, slug = sys.argv[1], sys.argv[2]
    source = VAULT_ROOT / vault_subpath
    if not source.exists():
        print(f"Not found in vault: {source}")
        sys.exit(1)

    dest_root = REPO_ROOT / "courses" / slug
    files = [source] if source.is_file() else sorted(source.rglob("*.md"))
    if not files:
        print(f"No .md files found under {source}")
        sys.exit(1)

    total_copied, total_missing = 0, 0
    for f in files:
        rel = f.name if source.is_file() else f.relative_to(source)
        out_path = dest_root / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        text = f.read_text(encoding="utf-8")
        converted, copied, missing = convert_note(text, out_path.parent / "images")
        out_path.write_text(converted, encoding="utf-8")
        total_copied += len(copied)
        total_missing += len(missing)
        print(f"{f.name}: imported -> {out_path.relative_to(REPO_ROOT)}"
              + (f" ({len(copied)} image(s))" if copied else ""))
        for m in missing:
            print(f"  ! could not find embedded file in vault: {m}")

    print(f"\nDone: {len(files)} note(s), {total_copied} image(s) copied"
          + (f", {total_missing} missing" if total_missing else "") + ".")
    print("Review with `git status` / `git diff`, then commit and push as usual.")


if __name__ == "__main__":
    main()
