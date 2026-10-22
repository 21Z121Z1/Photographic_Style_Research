"""Version-gated named cast selection over owned, hash-checked private tables."""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import numpy as np
from cast_prior import CastControls,CastTable,PriorResult,interpolate


@dataclass(frozen=True)
class NamedCast:
    name: str
    startup: bool=False


class OwnedCastBank:
    def __init__(self,private: Path,selection: Path,names: Path):
        self.private=private;self.selection=json.loads(selection.read_text());self.names=json.loads(names.read_text())
        for r in (self.selection,self.names):
            if r['hardware']!='iPhone17,3'or r['build']!='24A446':raise ValueError('Only the verified reference hardware/build is admitted')
        if self.selection['framework_uuid']!=self.names['framework_uuid']or not self.names['number_class_unsignedIntegerValue_implementation_verified']:
            raise ValueError('Matched framework and numeric getter proof required')
        if self.selection['cache_uuid']!='0094EE12-3B41-3892-A043-9459D9C749FE' or self.names['cache_uuid']!=self.selection['cache_uuid']:
            raise ValueError('Exact matched reference cache required')
        self.by_name={r['name']:r['cast_index']for r in self.names['rows']}
        if len(self.by_name)!=16 or set(self.by_name.values())!=set(range(1,17)):raise ValueError('Complete unambiguous cast-index map required')

    def evaluate(self,cast: NamedCast,controls: CastControls) -> PriorResult:
        if cast.name not in self.by_name or not isinstance(cast.startup,bool):raise ValueError('Known internal cast name and explicit bool startup required')
        hits=[r for r in self.selection['selection']if r['cast_index']==self.by_name[cast.name]and r['startup']==cast.startup]
        if len(hits)!=1:raise ValueError('Unambiguous static branch required')
        digest=hits[0]['table_sha256'];table=None
        if digest is not None:
            if len(digest)!=64 or any(c not in '0123456789abcdef'for c in digest):raise ValueError('Invalid private table digest')
            raw=(self.private/(digest+'.f32')).read_bytes()
            if len(raw)!=2400 or hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Private table source changed')
            table=CastTable(np.frombuffer(raw,dtype='<f4').reshape(5,5,2,3,4))
        return interpolate(controls,table,monochrome=cast.name in self.names['monochrome_cast_names'])


def check_named_paths(private: Path,selection: Path,names: Path,output: Path) -> dict:
    if output.exists():raise FileExistsError(output)
    bank=OwnedCastBank(private,selection,names);controls=CastControls(-.37,.42,.65,.8);rows=[]
    for name in bank.by_name:
        for startup in (False,True):
            result=bank.evaluate(NamedCast(name,startup),controls)
            rows.append({'name':name,'cast_index':bank.by_name[name],'startup':startup,'monochrome':name in bank.names['monochrome_cast_names'],
                         'fallback':result.lower_indices is None,'coefficient_sha256':hashlib.sha256(result.output_coefficients.tobytes()).hexdigest(),
                         'shader_packing_sha256':hashlib.sha256(result.shader_prior_matrix().tobytes()).hexdigest()})
    result={'scope':'New named-interface composition only; no original iOS/Metal execution and no accepted native batch rerun.',
            'hardware':'iPhone17,3','build':'24A446','cache_uuid':bank.names['cache_uuid'],'controls':controls.__dict__,
            'combinations':len(rows),'fallback_combinations':sum(r['fallback']for r in rows),
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'raw_tables_uploaded':False,'rows':rows}
    output.write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private',type=Path);p.add_argument('selection',type=Path);p.add_argument('names',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=check_named_paths(a.private,a.selection,a.names,a.output);print(json.dumps({'named_combinations':r['combinations'],'fallback_combinations':r['fallback_combinations']}))
