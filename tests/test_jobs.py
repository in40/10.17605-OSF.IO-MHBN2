import os
import time

from smoke_tui import jobs


def test_is_running_false_when_no_pidfile(tmp_path):
    assert jobs.is_running(str(tmp_path), "sys") is False


def test_is_running_stale_pidfile_is_cleaned(tmp_path):
    base = tmp_path / "sys"
    base.mkdir()
    (base / ".job.pid").write_text("999999999", encoding="utf-8")  # nonexistent pid
    assert jobs.is_running(str(tmp_path), "sys") is False
    assert not (base / ".job.pid").exists()  # stale pidfile removed


def test_start_and_stop(tmp_path):
    info = jobs.start(str(tmp_path), "sys", ["sleep", "30"])
    assert info["pid"] > 0
    assert jobs.is_running(str(tmp_path), "sys") is True
    assert jobs.stop(str(tmp_path), "sys") is True
    # give SIGTERM a moment to land
    for _ in range(20):
        if not jobs.is_running(str(tmp_path), "sys"):
            break
        time.sleep(0.1)
    assert jobs.is_running(str(tmp_path), "sys") is False


def test_start_refuses_when_already_running(tmp_path):
    jobs.start(str(tmp_path), "sys", ["sleep", "30"])
    try:
        jobs.start(str(tmp_path), "sys", ["sleep", "30"])
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass
    jobs.stop(str(tmp_path), "sys")


def test_progress_counts_summary_files(tmp_path):
    base = tmp_path / "sys" / "T1" / "r0p5"
    base.mkdir(parents=True)
    (base / "summary_0.txt").write_text("x", encoding="utf-8")
    (base / "summary_1.txt").write_text("y", encoding="utf-8")
    done, exp = jobs.progress(str(tmp_path), "sys", 10)
    assert done == 2
    assert exp == 10


def test_tail_returns_last_lines(tmp_path):
    base = tmp_path / "sys"
    base.mkdir()
    (base / ".job.log").write_text(
        "\n".join(f"line{i}" for i in range(100)), encoding="utf-8"
    )
    t = jobs.tail(str(tmp_path), "sys", n=5)
    assert t.splitlines() == ["line95", "line96", "line97", "line98", "line99"]


def test_tail_missing_log_is_empty(tmp_path):
    assert jobs.tail(str(tmp_path), "nosuch", 10) == ""
