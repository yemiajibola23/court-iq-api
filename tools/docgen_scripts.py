#!/usr/bin/env python3
"""
Script Docs Generator

What: Builds docs/SCRIPTS.md by collecting `--help` from repo scripts.
Why:  Keeps documentation accurate and teaches future-you how tools work.
Usage:
  python tools/docgen_scripts.py --out docs/SCRIPTS.md \
      --py-glob "tools/*.py" --sh-glob "scripts/*.sh"

Notes:
- A script that exits non-zero on --help is still included; we show whatever came out.
- Put a short "What/Why/Usage" docstring at the top of Python scripts for richer context.
"""
from __future__ import annotations
import argparse, subprocess, sys, shlex
from pathlib import Path

def run_help(cmd:list[str]) -> str:
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        return out.strip() or "(no help output)"
    except subprocess.CalledProcessError as e:
        return (e.output or "").strip() or "(no help output)"
    except FileNotFoundError:
        return "(command not found)"

def read_header(p: Path) -> str:
    """Return a short header from the file (first triple-quoted block for .py; first commented block for .sh)."""
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    if p.suffix == ".py":
        # naive first triple-quoted string
        import re
        m = re.search(r'^[ \t]*[ru]?\"\"\"(.*?)\"\"\"', text, flags=re.S|re.M|re.I)
        if not m:
            m = re.search(r"^[ \t]*[ru]?\'\'\'(.*?)\'\'\'", text, flags=re.S|re.M|re.I)
        return (m.group(1).strip() if m else "")
    if p.suffix in (".sh",):
        lines = []
        for line in text.splitlines():
            if line.startswith("#!"):
                continue
            if line.strip().startswith("#"):
                lines.append(line.strip("# ").rstrip())
            elif lines:
                break
        return "\n".join(lines).strip()
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/SCRIPTS.md")
    ap.add_argument("--py-glob", default="tools/*.py")
    ap.add_argument("--sh-glob", default="scripts/*.sh")
    args = ap.parse_args()

    out_lines = ["# Automation Scripts Reference", ""]
    root = Path(".")

    groups = [
        ("Python tools", sorted(root.glob(args.py_glob))),
        ("Shell scripts", sorted(root.glob(args.sh_glob))),
    ]

    for title, files in groups:
        if not files:
            continue
        out_lines += [f"## {title}", ""]
        for p in files:
            if p.name == Path(__file__).name:
                continue
            header = read_header(p)
            out_lines += [f"### `{p}`", ""]
            if header:
                out_lines += ["_Summary:_", "", header, ""]
            # build help command
            if p.suffix == ".py":
                cmd = [sys.executable, str(p), "--help"]
            else:
                # best-effort: run script with --help, allow non-executable by invoking bash
                cmd = ["bash", str(p), "--help"]
            out_lines += ["**`--help` output:**", "", "```text", run_help(cmd), "```", ""]
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out_lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
