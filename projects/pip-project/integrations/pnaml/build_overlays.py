"""Build minimal plugin overlay ZIPs from this private integration test stage."""
from pathlib import Path
import hashlib, json, zipfile

root = Path(__file__).resolve().parent
out = root / "dist"
out.mkdir(exist_ok=True)
for name in ("mobile", "semantic"):
    source = root / name
    manifest = json.loads((source / "OVERLAY_FILES.json").read_text())
    files = {p: (source / p).read_bytes() for p in manifest["files"]}
    if manifest["regenerate_sha256sums"]:
        # Preserve entries for untouched files, update only changed static files.
        old = (source / "SHA256SUMS.txt").read_text().splitlines()
        hashes = {}
        for line in old:
            if line.strip():
                digest, path = line.split("  ", 1)
                hashes[path] = digest
        for path, content in files.items():
            hashes[path] = hashlib.sha256(content).hexdigest()
        files["SHA256SUMS.txt"] = ("".join(f"{hashes[p]}  {p}\n" for p in sorted(hashes))).encode()
    target = out / f"pnaml-{name}-{manifest['version']}-overlay.zip"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, content in sorted(files.items()):
            archive.writestr(path, content)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(files)
        for path, content in files.items():
            assert archive.read(path) == content
    print(f"{target.name}: {len(files)} files, {target.stat().st_size} bytes")
