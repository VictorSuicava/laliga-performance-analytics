"""Package source, documentation and static previews for a standalone repository."""
from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ("README.md", ".gitignore", ".github", "pyproject.toml", "scripts", "sql", "tests", "docs", "powerbi", "output/pdf")


def shareable(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in ("__pycache__", ".pbi", ".cache") for part in relative.parts):
        return False
    if path.suffix.lower() in (".pyc", ".pyo", ".pbix", ".pbit"):
        return False
    if path.name == "model.bim":
        return False
    if relative.parts[:3] == ("powerbi", "LL.SemanticModel", "definition"):
        return False
    return True


def main() -> None:
    files = []
    for name in INCLUDE:
        path = ROOT / name
        files.extend([path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file()))
    files.extend(sorted(ROOT.glob("data/*/.gitkeep")))
    files = sorted(set(p for p in files if shareable(p)))
    output = ROOT / "output/release/laliga-performance-analytics.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    with ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archive integrity check failed")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".zip.sha256").write_text(f"{digest}  {output.name}\n", encoding="ascii")
    print(f"Packaged {len(files)} files: {output}")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()
