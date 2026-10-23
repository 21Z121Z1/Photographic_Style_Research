"""Drive the candidate's supported boundary and retain its exact-source receipt."""
import argparse
from pathlib import Path
import json

from execution import Study, Selection, RenderedModel

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / 'research/styles-firmware-20261022/evidence'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--intent', choices=('portable', 'apple-reference'), default='portable')
    parser.add_argument('--context', type=Path, default=EVIDENCE/'complete-context-s15a.json')
    parser.add_argument('--sealed-binary', type=Path)
    args = parser.parse_args()
    if args.intent == 'portable':
        study = Study.portable(ROOT, args.context, selection=Selection.BRIGHT16)
    else:
        if args.sealed_binary is None:
            parser.error('--sealed-binary must identify the original artifact')
        study = Study.reference(ROOT, args.context, EVIDENCE/'model-precision-v3-s25c6.json', args.sealed_binary)
    outcome = study.run(args.output)
    print(json.dumps({'outcome':type(outcome).__name__, 'receipt':str(args.output/'receipt.json')}))
    return 0 if isinstance(outcome, RenderedModel) else 2


if __name__ == '__main__':
    raise SystemExit(main())
