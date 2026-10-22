"""Eight additional two-leaf connection calls, separate from all-active calls.

This declared case-provider substitution reuses the complete original helper
compiler/checker without rerunning its already recorded 24 mixed cases.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import native_bgfg_complete_check as checker


def coupled_cases(block):
    profiles=[('local+gamma',{4:.05,5:.05}),('whites+underGrass',{0:.05,10:.05})]if block=='bg'else[('neck+underTone',{0:.35,14:.1,15:.1}),('lighten+smart',{0:.35,3:.05,8:.05})]
    for name,profile in profiles:
        for guide,person,skin in [(.4,.5,.3),(.7,.8,.6)]:
            yield name,checker.packet(block,profile),np.array([.2,.4,.8,guide,person,skin,.3,.5,.7],dtype='f2').astype('f4')


def check(source,output):
    previous=checker.cases
    try:
        checker.cases=coupled_cases;r=checker.check(source,output)
    finally:checker.cases=previous
    r['case_provider']={'declared_substitution':'native_bgfg_coupled_check.coupled_cases','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'all_active_mixed_24_cases_repeated':False}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
