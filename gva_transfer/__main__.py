import argparse
import json
from .commitment import freeze,verify
from .runner import execute

def main():
    parser=argparse.ArgumentParser(description='Bounded GVA transfer study; explicit frozen phase activation')
    sub=parser.add_subparsers(dest='command',required=True)
    seal=sub.add_parser('freeze');seal.add_argument('--phase',choices=['development','confirmation'],required=True)
    seal.add_argument('--output',required=True);seal.add_argument('--validation',required=True);seal.add_argument('--sample')
    check=sub.add_parser('verify');check.add_argument('--phase',choices=['development','confirmation'],required=True);check.add_argument('--freeze',required=True)
    run=sub.add_parser('run');run.add_argument('--phase',choices=['development','confirmation'],required=True)
    run.add_argument('--freeze',required=True);run.add_argument('--output',required=True);run.add_argument('--execute-phase',action='store_true');run.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    if args.command=='freeze':
        value=freeze(args.phase,args.output,args.validation,args.sample);result=dict(status=value['status'],source_hash=value['source_hash'],phase=args.phase)
    elif args.command=='verify':
        value=verify(args.freeze,args.phase);result=dict(status='VERIFIED',phase=args.phase,source_hash=value['source_hash'])
    else: result=execute(args.phase,args.freeze,args.output,args.resume,args.execute_phase)
    print(json.dumps(result))

if __name__=='__main__':main()
