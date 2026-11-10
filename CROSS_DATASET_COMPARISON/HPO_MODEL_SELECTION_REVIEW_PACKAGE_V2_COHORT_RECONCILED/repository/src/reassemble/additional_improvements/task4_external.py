"""Record one visual stage so a replacement coordinator can adopt it safely."""
import argparse
from datetime import datetime,timezone
import os
from pathlib import Path
import signal
import sys
import time
from types import SimpleNamespace
from .common import read,write


class ExternalVisual:
    def __init__(self,receipt):
        self.receipt=Path(receipt);self.pid=read(receipt)['pid']
    def poll(self):
        meta=read(self.receipt)
        if 'returncode' in meta:return meta['returncode']
        path=Path(f'/proc/{self.pid}/cmdline')
        if not path.exists():return 127
        try:argv=path.read_bytes().split(b'\0')
        except FileNotFoundError:return 127
        if b'reassemble.additional_improvements.task4_external' not in argv:return 126
        return None
    def send_signal(self,sig):
        if self.poll() is None:os.kill(self.pid,sig)
    def wait(self):
        while self.poll() is None:time.sleep(5)
        return self.poll()


def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--deadline',required=True);a=p.parse_args()
    meta=dict(stage='visual',pid=os.getpid(),external_visual=True,started_UTC=datetime.now(timezone.utc).isoformat(),command=sys.argv)
    write(a.receipt,meta)
    code=1
    try:
        from .corruption_resume import worker
        code=worker(SimpleNamespace(stage='visual',deadline=a.deadline))
    except SystemExit as exc:code=int(exc.code or 0)
    except BaseException as exc:
        meta['error']=repr(exc);raise
    finally:
        meta.update(returncode=code,finished_UTC=datetime.now(timezone.utc).isoformat());write(a.receipt,meta,replace=True)
    raise SystemExit(code)


if __name__=='__main__':main()
