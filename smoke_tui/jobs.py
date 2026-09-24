"""Background job control for long summarization passes.

A job runs **detached** (new session) so it survives the TUI. All status is
read from the filesystem (pidfile + output dir), so the TUI can reattach to
a running job after closing and reopening — there is no live pipe to lose.

Layout (per system, under the phase's summaries dir):
    <summ_dir>/<system>/.job.pid   running process id
    <summ_dir>/<system>/.job.log   captured stdout/stderr
    <summ_dir>/<system>/<text_id>/<level>/summary_*.txt   the work itself
"""
from __future__ import annotations

import os
import signal
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _paths(summ_dir: str, system: str) -> tuple[Path, Path]:
    base = Path(summ_dir) / str(system)
    return base / ".job.pid", base / ".job.log"


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def _is_zombie(pid: int) -> bool:
    """A finished-but-unreaped child still answers os.kill(pid,0); treat it as dead."""
    try:
        with open(f"/proc/{pid}/stat", encoding="ascii", errors="replace") as f:
            data = f.read()
        # format: pid (comm) state ...  — comm may contain spaces/parens
        rparen = data.rfind(")")
        return data[rparen + 2] == "Z"
    except (OSError, IndexError):
        return False


def read_pid(summ_dir: str, system: str) -> int | None:
    pid_file, _ = _paths(summ_dir, system)
    if not pid_file.exists():
        return None
    try:
        return int(pid_file.read_text().strip())
    except (ValueError, OSError):
        return None


def is_running(summ_dir: str, system: str) -> bool:
    pid = read_pid(summ_dir, system)
    if pid is None:
        return False
    if pid_alive(pid) and not _is_zombie(pid):
        return True
    # stale or zombie pidfile (process gone / finished) — clean it up
    pid_file, _ = _paths(summ_dir, system)
    try:
        pid_file.unlink()
    except OSError:
        pass
    return False


def start(summ_dir: str, system: str, cmd: list[str]) -> dict:
    """Launch a detached job. Raises RuntimeError if one is already running."""
    if is_running(summ_dir, system):
        raise RuntimeError(f"a job is already running for '{system}'")
    pid_file, log_file = _paths(summ_dir, system)
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    logf = open(log_file, "ab")
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(REPO),
            stdout=logf,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    finally:
        logf.close()  # the child holds its own fd
    pid_file.write_text(str(proc.pid))
    return {"pid": proc.pid, "log": str(log_file)}


def stop(summ_dir: str, system: str) -> bool:
    """Terminate a running job via its pidfile. Returns True if a job was stopped."""
    pid = read_pid(summ_dir, system)
    pid_file, _ = _paths(summ_dir, system)
    if pid is None:
        return False
    if pid_alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        pid_file.unlink()
    except OSError:
        pass
    return True


def progress(summ_dir: str, system: str, expected: int) -> tuple[int, int]:
    base = Path(summ_dir) / str(system)
    done = len(list(base.rglob("summary_*.txt"))) if base.exists() else 0
    return done, expected


def tail(summ_dir: str, system: str, n: int = 30) -> str:
    _, log_file = _paths(summ_dir, system)
    if not log_file.exists():
        return ""
    lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-n:])
