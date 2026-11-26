"""Researcher-authorized fit-boundary stop; does not modify frozen training code.

The next fit's existing nonblocking single-writer lock prevents a race between
the current fit returning and the controller attempting another fit. Contention
ends the original controller before it can configure or train that next fit.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
REPO = STUDY.parents[2]
RUNTIME = STUDY / "13_reproducibility/runtime"


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".writing.{os.getpid()}")
    with temporary.open("w") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def proc_identity(pid, proc_root=Path("/proc")):
    root = proc_root / str(pid)
    try:
        fields = (root / "stat").read_text().rsplit(")", 1)[1].split()
        return {"pid": pid, "start_ticks": int(fields[19]), "state": fields[0],
                "cmdline": [s.decode() for s in (root / "cmdline").read_bytes().split(b"\0") if s],
                "cwd": str((root / "cwd").readlink())}
    except (FileNotFoundError, ProcessLookupError):
        return None


def same_process(expected, actual):
    return bool(actual and actual["state"] != "Z" and all(
        actual.get(k) == expected.get(k) for k in ("pid", "start_ticks", "cmdline", "cwd")))


def alive(expected):
    return same_process(expected, proc_identity(expected["pid"]))


def send(expected, sig):
    """PID descriptor plus creation identity prevents signalling a reused PID."""
    try:
        descriptor = os.pidfd_open(expected["pid"])
    except ProcessLookupError:
        return False
    try:
        if not alive(expected):
            return False
        signal.pidfd_send_signal(descriptor, sig)
        return True
    finally:
        os.close(descriptor)


def acquire(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = path.open("a+")
    try:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException:
        stream.close()
        raise
    return stream


def snapshot(name):
    folder = HERE / name
    folder.mkdir(exist_ok=False)
    paths = list((STUDY / "14_final_research_reports").glob("*.md"))
    paths += [STUDY / "VIFAILBACK_MATCHED_CNN_STUDY_STATUS.md"]
    paths += list((STUDY / "11_metrics_and_statistics").glob("*.json"))
    paths += [RUNTIME / n for n in ["GPU_CONTROLLER_STATUS.json", "GPU_COMPLETED_FITS.json", "WATCH_STATUS.json"]]
    manifest = []
    for path in paths:
        if path.is_file():
            relative = path.relative_to(STUDY)
            target = folder / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            manifest.append({"source": str(relative), "snapshot": str(target.relative_to(HERE)),
                             "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    write(folder / "SNAPSHOT_MANIFEST.json", {"utc": utc(), "files": manifest})


def completed_target(request):
    root = STUDY / request["target_fit"]
    path = root / "COMPLETE.json"
    if not path.exists():
        return None
    receipt = read(path)
    for key, expected in [("condition", "FULL20"), ("seed", 42),
                          ("fit_id", "outer0_inner2"), ("executed_epochs", 20)]:
        if receipt.get(key) != expected:
            raise ValueError(f"Target completion mismatch: {key}")
    history = read(root / "HISTORY.json")
    if [row["epoch"] for row in history] != list(range(1, 21)):
        raise ValueError("Target does not have the complete twenty-epoch history")
    for name, key in [("HISTORY.json", "history_sha256"),
                      ("predictions.json", "prediction_sha256")]:
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != receipt[key]:
            raise ValueError(f"Target completion hash mismatch: {name}")
    return receipt


def stopped_receipt(request, target, interrupted=False):
    next_root = STUDY / request["blocked_next_fit"]
    unexpected = [str(p.relative_to(STUDY)) for p in next_root.iterdir() if p.name != "FIT.lock"]
    if unexpected:
        raise RuntimeError(f"Unexpected next-fit outputs: {unexpected}")
    return {"utc": utc(), "status": "STOPPED_BY_RESEARCHER_AFTER_CURRENT_FIT" if target else "STOPPED_BEFORE_CURRENT_FIT_COMPLETED",
            "authorization": request["authorization"], "target_fit": request["target_fit"],
            "target_complete": bool(target), "target_completed_utc": target.get("completed_utc") if target else None,
            "blocked_next_fit": request["blocked_next_fit"], "next_fit_training_started": False,
            "placeholder_directory": "Contains only FIT.lock, created for the administrative stop; not a scientific fit attempt.",
            "controller_alive": alive(request["controller"]), "watcher_alive": alive(request["watcher"]),
            "controller_interrupt_required": interrupted, "do_not_resume_training": True,
            "unexecuted_fits_are_not_negative_model_results": True,
            "controller_lock_contention_if_recorded_is_intentional_stop_not_model_failure": True}


def remaining_seconds(deadline):
    return max(0., deadline - time.time())


def bounded_command(command, deadline, log_name):
    remaining = remaining_seconds(deadline)
    if remaining <= 0:
        return {"command": command, "status": "NOT_RUN_DEADLINE_REACHED"}
    with (HERE / log_name).open("xb") as log:
        child = subprocess.Popen(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT,
                                 start_new_session=True,
                                 env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "CUDA_VISIBLE_DEVICES": "",
                                      "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2",
                                      "NUMEXPR_NUM_THREADS": "2"})
        began = time.time()
        write(HERE / "ANALYSIS_CHILD.json", {"utc": utc(), "pid": child.pid,
                                             "command": command, "deadline_epoch": deadline})
        try:
            code = child.wait(timeout=remaining)
            return {"command": command, "exit_code": code, "seconds": time.time()-began,
                    "status": "COMPLETE" if code == 0 else "FAILED", "log": log_name}
        except subprocess.TimeoutExpired:
            # This is a new, directly owned CPU-only analysis child, never a training worker.
            child.terminate()
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=10)
            return {"command": command, "status": "STOPPED_AT_THREE_HOUR_DEADLINE",
                    "seconds": time.time()-began, "log": log_name}


def main():
    request = read(HERE / "CONTROL_REQUEST.json")
    controller = request["controller"]
    if not alive(controller):
        raise RuntimeError("Authorized controller identity is no longer active; do not arm against another process")
    current = read(RUNTIME / "GPU_CONTROLLER_STATUS.json")
    if (current.get("condition"), current.get("seed"), current.get("fit_id")) != ("FULL20", 42, "outer0_inner2"):
        raise RuntimeError("Current fit changed before arming")
    own_lock = acquire(HERE / "guard.lock")
    next_lock = acquire(STUDY / request["blocked_next_fit"] / "FIT.lock")
    try:
        write(HERE / "GUARD_STATUS.json", {"utc": utc(), "stage": "ARMED_WAITING_CURRENT_FIT",
              "guard": proc_identity(os.getpid()), "blocked_next_fit": request["blocked_next_fit"],
              "current_fit_unchanged": True, "postfit_max_seconds": request["postfit_max_seconds"]})
        snapshot("before_stop")
        target = None
        while True:
            target = completed_target(request)
            if target or not alive(controller):
                break
            time.sleep(2)
        completed_epoch = (dt.datetime.fromisoformat(target["completed_utc"]).timestamp()
                           if target else time.time())
        deadline = completed_epoch + request["postfit_max_seconds"]
        write(HERE / "GUARD_STATUS.json", {"utc": utc(), "stage": "FIT_FINISHED_STOPPING_CONTROLLER" if target else "CONTROLLER_EXITED_BEFORE_COMPLETION",
              "target_complete": bool(target), "deadline_utc": dt.datetime.fromtimestamp(deadline, dt.timezone.utc).isoformat()})
        # The blocked next-fit lock normally makes the original controller exit itself.
        # Only interrupt if its journal proves fit() returned, or at the hard deadline.
        interrupted = False
        while alive(controller):
            index = read(RUNTIME / "GPU_COMPLETED_FITS.json")
            returned = any(x.get("condition") == "FULL20" and x.get("seed") == 42 and
                           x.get("fit_id") == "outer0_inner2" for x in index)
            if (returned and time.time() - completed_epoch > 30) or remaining_seconds(deadline) <= 0:
                interrupted = send(controller, signal.SIGINT) or interrupted
            time.sleep(1)
        # The existing watcher performs its final safe evaluation, then exits when it
        # observes the deliberately stopped controller. No watcher launches training.
        while alive(request["watcher"]) and remaining_seconds(deadline) > 180:
            time.sleep(2)
        if alive(request["watcher"]):
            send(request["watcher"], signal.SIGINT)
            for _ in range(15):
                if not alive(request["watcher"]):
                    break
                time.sleep(1)
            if alive(request["watcher"]):
                send(request["watcher"], signal.SIGTERM)
        stop = stopped_receipt(request, target, interrupted)
        write(HERE / "STOP_RECEIPT.json", stop)
        snapshot("after_training_stop")
        command = [str(REPO / "ma_thesis_env/bin/python"), "-B", str(STUDY / "scripts/study.py"), "evaluate"]
        analysis = bounded_command(command, deadline-60, "evaluate.log")
        # This independent saved-score analysis never imports a model or reads raw videos.
        independent = bounded_command([str(REPO / "ma_thesis_env/bin/python"), "-B",
                                       str(HERE / "analyze_completed.py")], deadline-20, "analysis.log")
        snapshot("final_evidence")
        write(HERE / "FINAL_STATUS.json", {"utc": utc(), **stop,
              "analysis": analysis, "independent_analysis": independent,
              "deadline_utc": dt.datetime.fromtimestamp(deadline, dt.timezone.utc).isoformat(),
              "seconds_after_fit_completion": time.time()-completed_epoch,
              "three_hour_limit_observed": time.time() <= deadline,
              "stage": "CLOSED_COMPLETED_SCOPE" if analysis["status"] == independent["status"] == "COMPLETE" else "STOPPED_ANALYSIS_PARTIAL"})
        write(HERE / "GUARD_STATUS.json", {"utc": utc(), "stage": "FINISHED", "training_resume_authorized": False})
    finally:
        # Retain the guard while the original controller is capable of training.
        if alive(controller):
            write(HERE / "GUARD_ERROR.json", {"utc": utc(), "error": "Guard failed; retaining next-fit lock until controller exits"})
            while alive(controller):
                time.sleep(10)
        next_lock.close()
        own_lock.close()


if __name__ == "__main__":
    main()
