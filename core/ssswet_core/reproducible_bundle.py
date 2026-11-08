"""Deterministic, bounded ZIP bundles for explicitly selected research artifacts."""
from __future__ import annotations

from hashlib import sha256
import io
import json
import re
import stat
import zipfile

MAX_FILES = 100
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_BYTES = 20 * 1024 * 1024
MAX_ARCHIVE_BYTES = 25 * 1024 * 1024
_DENIED_SEGMENTS = {".ssh", "secrets", "credentials", "private"}
_PRIVATE_KEY = re.compile(br"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")


def _safe_path(path: object) -> str:
    if not isinstance(path, str) or not path or len(path) > 240 or "\\" in path or "\x00" in path:
        raise ValueError("artifact paths must be short relative POSIX paths")
    parts = path.split("/")
    if any(part in {"", ".", ".."} for part in parts) or path.startswith("/"):
        raise ValueError("artifact path traversal is not allowed")
    if any(part.lower() in _DENIED_SEGMENTS or part.lower() in {".env", "id_rsa", "id_ed25519"} for part in parts):
        raise ValueError("sensitive artifact paths are not allowed")
    if parts[-1].lower().endswith((".pem", ".key")):
        raise ValueError("private-key file extensions are not allowed")
    return path


def build_bundle(files: dict[str, str | bytes]) -> bytes:
    if not isinstance(files, dict) or not 1 <= len(files) <= MAX_FILES:
        raise ValueError(f"files must contain 1 to {MAX_FILES} explicitly selected artifacts")
    normalized, total = {}, 0
    for path, content in files.items():
        safe = _safe_path(path)
        if safe == "MANIFEST.json":
            raise ValueError("MANIFEST.json is reserved for the generated integrity manifest")
        if isinstance(content, str):
            payload = content.encode("utf-8")
        elif isinstance(content, bytes):
            payload = content
        else:
            raise ValueError("artifact content must be UTF-8 text or bytes")
        if len(payload) > MAX_FILE_BYTES:
            raise ValueError(f"artifact {safe} exceeds the per-file size limit")
        if _PRIVATE_KEY.search(payload):
            raise ValueError(f"artifact {safe} appears to contain a private key")
        total += len(payload)
        if total > MAX_TOTAL_BYTES:
            raise ValueError("selected artifacts exceed the total uncompressed size limit")
        normalized[safe] = payload
    manifest = {
        "schema_version": 1,
        "files": [
            {"path": path, "size_bytes": len(payload), "sha256": sha256(payload).hexdigest()}
            for path, payload in sorted(normalized.items())
        ],
        "explicit_selection_required": True,
        "secret_scanning_is_not_comprehensive": True,
    }
    manifest_bytes = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        entries = {**normalized, "MANIFEST.json": manifest_bytes}
        for path, payload in sorted(entries.items()):
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits = 0
            archive.writestr(info, payload, compress_type=zipfile.ZIP_STORED)
    result = output.getvalue()
    if len(result) > MAX_ARCHIVE_BYTES:
        raise ValueError("compressed bundle exceeds the archive size limit")
    return result


def verify_bundle(bundle: bytes) -> dict:
    if not isinstance(bundle, bytes) or len(bundle) > MAX_ARCHIVE_BYTES:
        raise ValueError("bundle must be bytes within the archive size limit")
    try:
        with zipfile.ZipFile(io.BytesIO(bundle), "r") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) > MAX_FILES + 1 or len(names) != len(set(names)):
                raise ValueError("bundle has duplicate names or too many entries")
            for info in infos:
                _safe_path(info.filename)
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(mode):
                    raise ValueError("symbolic links are not allowed in research bundles")
                if info.file_size > MAX_FILE_BYTES:
                    raise ValueError("bundle entry exceeds the per-file size limit")
            if sum(info.file_size for info in infos) > MAX_TOTAL_BYTES + MAX_FILE_BYTES:
                raise ValueError("bundle exceeds the total declared size limit")
            if "MANIFEST.json" not in names:
                raise ValueError("bundle manifest is missing")
            if infos[names.index("MANIFEST.json")].file_size > 100_000:
                raise ValueError("bundle manifest exceeds its size limit")
            manifest = json.loads(archive.read("MANIFEST.json").decode("utf-8"))
            if not isinstance(manifest, dict) or manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), list):
                raise ValueError("unsupported bundle manifest")
            expected = {item.get("path"): item for item in manifest["files"] if isinstance(item, dict)}
            if len(expected) != len(manifest["files"]):
                raise ValueError("bundle manifest contains duplicate or invalid entries")
            for path in expected:
                _safe_path(path)
            actual_names = set(names) - {"MANIFEST.json"}
            if set(expected) != actual_names:
                raise ValueError("bundle contents do not match the manifest")
            total = 0
            for name in sorted(actual_names):
                payload = archive.read(name)
                total += len(payload)
                item = expected[name]
                if len(payload) > MAX_FILE_BYTES or item.get("size_bytes") != len(payload) or item.get("sha256") != sha256(payload).hexdigest():
                    return {"valid": False, "reason": "size_or_digest_mismatch", "file": name}
            if total > MAX_TOTAL_BYTES:
                raise ValueError("bundle exceeds the total uncompressed size limit")
            return {"valid": True, "file_count": len(actual_names), "total_size_bytes": total, "manifest_sha256": sha256(archive.read("MANIFEST.json")).hexdigest()}
    except zipfile.BadZipFile as exc:
        raise ValueError("bundle is not a valid ZIP archive") from exc
