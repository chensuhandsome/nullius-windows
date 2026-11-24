"""Distribute the same native Windows support bytes with independent skills."""
from __future__ import annotations

import hashlib
import pathlib
import shutil

from .source_payload import validate_payload_file


_FILESYSTEM_SKILLS = {"research-harness", "research-team", "review-swarm"}
_PROCESS_SKILLS = _FILESYSTEM_SKILLS | {
    "claude-cli-runner", "dsh-cli-runner", "gemini-cli-runner", "kimi-cli-runner", "opencode-cli-runner",
}


def copy_windows_runtime(source_dir: pathlib.Path, target_dir: pathlib.Path) -> dict[str, str]:
    # Catalog skill sources are exactly <workspace>/skills/<skill>. External
    # catalogs without these platform assets remain independent of Nullius.
    skill = source_dir.name
    if skill not in _PROCESS_SKILLS:
        return {}
    source_root = source_dir.parent.parent
    support = source_root / "packages/shared/python/nullius_windows"
    if not support.is_dir():
        return {}
    if support.is_symlink() or not support.resolve().is_relative_to(source_root.resolve()):
        raise RuntimeError("Windows runtime source escapes its workspace")
    modules = ["__init__.py", "process.py"]
    if skill in _FILESYSTEM_SKILLS:
        modules.append("filesystem.py")
    hashes: dict[str, str] = {}
    for module in modules:
        original = support / module
        relative = pathlib.PurePosixPath("scripts/_runtime/nullius_windows") / original.name
        if original.is_symlink():
            raise RuntimeError("Windows runtime source must not contain symlinks")
        validate_payload_file(original, relative)
        target = target_dir.joinpath(*relative.parts)
        if target.exists() or target.is_symlink():
            raise RuntimeError(f"platform runtime collides with selected payload: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, target, follow_symlinks=False)
        hashes[relative.as_posix()] = hashlib.sha256(target.read_bytes()).hexdigest()
    return hashes
