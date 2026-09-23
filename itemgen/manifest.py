"""SHA-256 manifest for frozen items (pre-reg: freeze items + manifest)."""
from __future__ import annotations

import hashlib
import json


def hash_item(item: dict) -> str:
    canon = json.dumps(item, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def build_manifest(items_by_text: dict[str, dict[str, list[dict]]]) -> dict:
    """Map text_id -> {kind: [item hashes], combined: hash}."""
    manifest: dict = {}
    for tid, kinds in items_by_text.items():
        entry: dict = {}
        all_hashes: list[str] = []
        for kind, items in kinds.items():
            hs = [hash_item(i) for i in items]
            entry[kind] = hs
            all_hashes.extend(hs)
        entry["combined"] = hashlib.sha256(
            "".join(sorted(all_hashes)).encode("utf-8")
        ).hexdigest()
        manifest[tid] = entry
    return manifest


def manifest_digest(manifest: dict) -> str:
    canon = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()
