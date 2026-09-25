import subprocess
import sys
from pathlib import Path
from gva1.common import atomic_json,digest,sha,utc
from . import ROOT
from .commitment import source,runtime
from .model import require

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    folder=Path(args.output);folder.mkdir(parents=True,exist_ok=False)
    before=source()
    run=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests/transfer','-v'],cwd=ROOT,capture_output=True,text=True)
    (folder/'tests.txt').write_text(run.stdout+run.stderr,encoding='utf-8')
    print(run.stdout+run.stderr,flush=True)
    require(run.returncode==0,'Transfer preflight tests failed')
    require(source()==before,'Source changed during tests')
    record=dict(status='PASSED',utc=utc(),source_hash=digest(before),runtime=runtime(),test_log_sha256=sha(folder/'tests.txt'),
        new_transfer_roots_executed=0,external_review=False,scope='Deterministic fixtures and archived GVA-1 development roots only')
    atomic_json(folder/'VALIDATION.json',record)
    print(record)

if __name__=='__main__':main()
