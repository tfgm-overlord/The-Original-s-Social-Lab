from __future__ import annotations
import base64, hashlib, pathlib, zipfile

ROOT = pathlib.Path(__file__).resolve().parent
PACKAGE = ROOT / "tfgm_state_integrity"
DIST = ROOT.parent / "dist"
NAME = "tfgm_state_integrity"
VERSION = "0.1.0"
DIST_INFO = f"{NAME}-{VERSION}.dist-info"
WHEEL_NAME = f"{NAME}-{VERSION}-py3-none-any.whl"

def record_hash(data: bytes) -> str:
    return "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")

def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    target = DIST / WHEEL_NAME
    files: dict[str, bytes] = {}
    for path in PACKAGE.rglob("*"):
        if path.is_file() and path.name != WHEEL_NAME:
            rel = path.relative_to(ROOT).as_posix()
            files[rel] = path.read_bytes()
    metadata = (
        "Metadata-Version: 2.1\n"
        f"Name: {NAME}\n"
        f"Version: {VERSION}\n"
        "Summary: Public mirror of TFGM Warrant, State Integrity, and provenance primitives\n"
        "Requires-Python: >=3.10\n"
    ).encode()
    wheel = b"Wheel-Version: 1.0\nGenerator: tfgm-public-lab-build\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
    files[f"{DIST_INFO}/METADATA"] = metadata
    files[f"{DIST_INFO}/WHEEL"] = wheel
    records = []
    for name, data in sorted(files.items()):
        records.append(f"{name},{record_hash(data)},{len(data)}")
    records.append(f"{DIST_INFO}/RECORD,,")
    files[f"{DIST_INFO}/RECORD"] = ("\n".join(records) + "\n").encode()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in sorted(files.items()):
            zf.writestr(name, data)
    print(target)

if __name__ == "__main__":
    main()
