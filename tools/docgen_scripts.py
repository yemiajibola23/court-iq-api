#!/usr/bin/env python3
"""
Script Docs Generator (polished)

Features:
- Contents section with explicit, stable anchors (works in VSCode & GitHub)
- "Source:" link on its own line (no nested backticks in headers)
- Deterministic ordering by filename
- Clamp long --help output (default 60 lines) to keep docs readable
- Optional GitHub linkification via --repo-url / --default-branch

Usage:
  python tools/docgen_scripts.py \
      --out docs/SCRIPTS.md \
      --py-glob "tools/*.py" \
      --sh-glob "scripts/*.sh" \
      --clamp 60 \
      [--repo-url https://github.com/OWNER/REPO] \
      [--default-branch main]
"""
from __future__ import annotations
import argparse, subprocess, sys, re
from pathlib import Path
from datetime import datetime
import tempfile, filecmp, difflib


def run_help(cmd: list[str]) -> str:
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        return out.strip()
    except subprocess.CalledProcessError as e:
        return (e.output or "").strip()
    except FileNotFoundError:
        return "(command not found)"

def clamp(text: str, n: int) -> str:
    lines = (text or "").splitlines()
    return "\n".join(lines[:n] + (["… (truncated)"] if len(lines) > n else []))

def read_header(p: Path) -> str:
    try:
        src = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    if p.suffix == ".py":
        m = re.search(r'^[ \t]*[ru]?"""(.*?)"""', src, flags=re.S|re.M|re.I)
        if not m:
            m = re.search(r"^[ \t]*[ru]?'''(.*?)'''", src, flags=re.S|re.M|re.I)
        return (m.group(1).strip() if m else "")
    if p.suffix == ".sh":
        lines, seen = [], False
        for line in src.splitlines():
            if line.startswith("#!"):
                continue
            if line.strip().startswith("#"):
                lines.append(line.strip("# ").rstrip())
                seen = True
            elif seen:
                break
        return "\n".join(lines).strip()
    return ""

def make_anchor_id(path: str) -> str:
    # Stable, renderer-agnostic id (no nesting/backticks).
    base = path.lower().replace("/", "-").replace(".", "-")
    base = re.sub(r"[^a-z0-9\-]+", "-", base)
    base = re.sub(r"-{2,}", "-", base).strip("-")
    return f"sec-{base}"

def gh_link(path: str, repo_url: str|None, branch: str) -> str:
    if repo_url:
        return f"{repo_url.rstrip('/')}/blob/{branch}/{path}"
    return path  # relative link

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/SCRIPTS.md")
    ap.add_argument("--py-glob", default="tools/*.py")
    ap.add_argument("--sh-glob", default="scripts/*.sh")
    ap.add_argument("--clamp", type=int, default=60)
    ap.add_argument("--repo-url", default=None, help="e.g. https://github.com/OWNER/REPO")
    ap.add_argument("--default-branch", default="dev")
    ap.add_argument("--check", action="store_true", help="Check if output would change; do not write; exit 1 if different")
    args = ap.parse_args()

    root = Path(".")
    py_files = sorted(root.glob(args.py_glob), key=lambda p: p.name)
    sh_files = sorted(root.glob(args.sh_glob), key=lambda p: p.name)

    sections = []
    toc = ["## Contents"]
    if py_files:
        toc.append("- [Python tools](#python-tools)")
        for f in py_files:
            toc.append(f"  - [{f}](#{make_anchor_id(str(f))})")
    if sh_files:
        toc.append("- [Shell scripts](#shell-scripts)")
        for f in sh_files:
            toc.append(f"  - [{f}](#{make_anchor_id(str(f))})")

    out_lines = ["# Automation Scripts Reference", "", *toc, ""]

    # Python tools
    if py_files:
        out_lines += ["## Python tools", ""]
        for p in py_files:
            anchor = make_anchor_id(str(p))
            header = read_header(p)
            out_lines += [
                f"### `{p}`",
                f'<a id="{anchor}"></a>',
                f"_Source: [{p}]({gh_link(str(p), args.repo_url, args.default_branch)})_",
                "",
            ]
            if header:
                out_lines += ["_Summary:_", "", header, ""]
            help_out = run_help([sys.executable, str(p), "--help"])
            help_block = clamp(help_out or "(no help output)", args.clamp)
            out_lines += ["**`--help` output:**", "", "```text", help_block, "```", ""]

    # Shell scripts
    if sh_files:
        out_lines += ["## Shell scripts", ""]
        for p in sh_files:
            anchor = make_anchor_id(str(p))
            header = read_header(p)
            out_lines += [
                f"### `{p}`",
                f'<a id="{anchor}"></a>',
                f"_Source: [{p}]({gh_link(str(p), args.repo_url, args.default_branch)})_",
                "",
            ]
            # Prefer a quick --help probe; if script lacks it, don't execute the body.
            probe = run_help(["bash", str(p), "--help"])
            help_out = probe or "(no help output)"
            if header:
                out_lines += ["_Summary:_", "", header, ""]
            out_lines += ["**`--help` output:**", "", "```text", clamp(help_out, args.clamp), "```", ""]

        # Footer (string) and body assembly
        FOOTER = f"---\n_Generated on {datetime.now().isoformat(timespec='seconds')}_\n"

        # Do NOT include footer in the body we compare
        body_text = "\n".join(out_lines).rstrip() + "\n"

        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Helper to strip an existing footer for comparison
        FOOTER_RE = re.compile(r"\n---\n_Generated on .*\n\Z", re.DOTALL)

        def strip_footer(text: str) -> str:
            return FOOTER_RE.sub("", text).rstrip() + "\n" if text else ""

        if args.check:
            # Compare body-only (ignore footer differences)
            disk_text = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
            disk_body = strip_footer(disk_text)

            if disk_body == body_text:
                print(f"OK: {args.out} is up-to-date")
                sys.exit(0)
            else:
                print(f"NEEDS UPDATE: {args.out} would change")
                old = disk_body.splitlines()
                new = body_text.splitlines()
                for i, line in enumerate(difflib.unified_diff(old, new, fromfile=args.out, tofile=f"{args.out} (new)")):
                    if i > 120:
                        print("... (diff truncated)")
                        break
                    print(line)
                sys.exit(1)

        # Write mode: write body + fresh footer
        final_text = body_text + FOOTER
        out_path.write_text(final_text, encoding="utf-8")
        print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
