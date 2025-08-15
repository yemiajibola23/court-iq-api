#!/usr/bin/env python3
from __future__ import annotations
import sys, glob
from pathlib import Path
import yaml  # pip install pyyaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "meta" / "project_structure.yml"

def load_manifest():
    if not MANIFEST.exists():
        print(f"❌ Missing manifest: {MANIFEST}")
        sys.exit(1)
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "project" not in data:
        print("❌ Invalid manifest format. Expecting top-level 'project' key.")
        sys.exit(1)
    return data["project"]

def check_paths(required: list[str], allow_globs: list[str]) -> tuple[list[str], list[str]]:
    """Return (missing, satisfied) for required paths. Globs are satisfied if at least one match exists."""
    missing = []
    satisfied = []
    for entry in required:
        if "*" in entry:
            # treat as glob regardless of allow_globs
            matches = glob.glob(str(ROOT / entry), recursive=True)
            if matches:
                satisfied.append(entry)
            else:
                missing.append(entry + " (glob had no matches)")
        else:
            p = ROOT / entry
            if p.exists():
                satisfied.append(entry)
            else:
                # If entry is allowed to be satisfied by globs_ok, check those too
                if any(glob.glob(str(ROOT / g), recursive=True) for g in allow_globs if g == entry):
                    satisfied.append(entry)
                else:
                    missing.append(entry)
    return missing, satisfied

def main():
    proj = load_manifest()
    req_dirs = proj.get("required_dirs", [])
    req_files = proj.get("required_files", [])
    opt_files = proj.get("optional_files", [])
    globs_ok = proj.get("globs_ok", [])

    errors = []

    # Check directories
    missing_dirs = []
    for d in req_dirs:
        p = ROOT / d
        if not p.exists() or not p.is_dir():
            missing_dirs.append(d)
    if missing_dirs:
        errors.append("Missing required directories:\n  - " + "\n  - ".join(missing_dirs))

    # Check files (supports '*' globs)
    missing_files = []
    for f in req_files:
        if "*" in f:
            matches = glob.glob(str(ROOT / f), recursive=True)
            if not matches:
                missing_files.append(f + " (glob had no matches)")
        else:
            p = ROOT / f
            if not p.exists() or not p.is_file():
                missing_files.append(f)

    # Optional files: just warn (don’t fail)
    missing_optional = []
    for f in opt_files:
        if "*" in f:
            matches = glob.glob(str(ROOT / f), recursive=True)
            if not matches:
                missing_optional.append(f + " (glob had no matches)")
        else:
            p = ROOT / f
            if not p.exists():
                missing_optional.append(f)

    if missing_files:
        errors.append("Missing required files:\n  - " + "\n  - ".join(missing_files))

    if errors:
        print("❌ Structure validation failed:")
        for e in errors:
            print(e)
        if missing_optional:
            print("\nℹ️ Optional files not found (FYI, not fatal):")
            for f in missing_optional:
                print("  -", f)
        sys.exit(1)

    print("✅ Structure validation passed.")
    if missing_optional:
        print("\nℹ️ Optional files not found (FYI, not fatal):")
        for f in missing_optional:
            print("  -", f)

if __name__ == "__main__":
    main()
