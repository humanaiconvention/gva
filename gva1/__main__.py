import argparse
import json
from .common import require
from .design import development, confirmation
from .freeze import create_freeze, validate_freeze
from .runner import execute

def main():
    parser = argparse.ArgumentParser(description='GVA-1 execution: preparation never evaluates reserved confirmation roots')
    sub = parser.add_subparsers(dest='operation', required=True)
    dev = sub.add_parser('development-replay'); dev.add_argument('--output', required=True); dev.add_argument('--resume', action='store_true')
    freeze = sub.add_parser('freeze'); freeze.add_argument('--preflight', required=True); freeze.add_argument('--output', required=True)
    verify = sub.add_parser('verify-freeze'); verify.add_argument('--freeze', required=True)
    run = sub.add_parser('run-confirmation'); run.add_argument('--freeze', required=True); run.add_argument('--output', required=True)
    run.add_argument('--execute-confirmation', action='store_true'); run.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.operation == 'development-replay':
        result = execute(development(), args.output, resume=args.resume)
    elif args.operation == 'freeze':
        result = create_freeze(args.output, args.preflight)
        result = {k: result[k] for k in ('status', 'source_hash', 'confirmation_outcomes_generated')}
    elif args.operation == 'verify-freeze':
        result = validate_freeze(args.freeze)
        result = dict(status='VERIFIED', source_hash=result['source_hash'], confirmation_outcomes_generated=0)
    else:
        require(args.execute_confirmation, 'No confirmation execution requested')
        result = execute(confirmation(), args.output, resume=args.resume, freeze_path=args.freeze, execute_confirmation=True)
    print(json.dumps(result))

if __name__ == '__main__':
    main()
