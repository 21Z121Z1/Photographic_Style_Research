"""Convert a user-selected image using original Apple SPI on macOS 27."""
import argparse
import json
from pathlib import Path
import subprocess

from matrix import compile_tools,generate_case,require,source_head


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--max-dimension',type=int,default=1024,choices=[512,1024,1536,2048,4096])
    args=parser.parse_args()
    source=args.input.resolve();out=args.output.resolve()
    if not source.is_file():parser.error('input must be an existing image file')
    if out.exists() and any(out.iterdir()):parser.error('output directory must be empty')
    out.mkdir(parents=True,exist_ok=True)
    head=source_head()
    build=out/'_build';compile_tools(build,'generate')
    require([build/'prepare',source,out,args.max_dimension],out,'prepare')
    receipt=generate_case(out,build,head)
    print(json.dumps({'candidate':str(out/'texture-candidate.heic'),'receipt':str(out/'acceptance.json'),
                      'stored_people':receipt['stored_person_count'],'cloud_native_checks_passed':receipt['passed'],
                      'device_activation':receipt['device_activation']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
