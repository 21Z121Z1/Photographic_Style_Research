"""Runner-only reuse of unchanged S89 actual-carrier validation statements."""
from pathlib import Path
import ast,hashlib,json,math
import numpy as np
import PyOpenColorIO as ocio
from PIL import Image,ImageDraw
from tools.heif_dump import parse_heif
Y=np.array([.2289745641,.6917385218,.0792869141]);ROWS=32
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
    with Path(p).open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def selected_modules(source):
    tree=ast.parse(source);loop=next(n for n in tree.body if isinstance(n,ast.For)and ast.unparse(n.iter)=='input_rows');attempt=next(n for n in loop.body if isinstance(n,ast.Try))
    body=[n for n in attempt.body if n.lineno>=64 and n.end_lineno<=84];assert body and body[0].lineno==64 and body[-1].end_lineno==84
    start=next(i for i,n in enumerate(tree.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='cfg'for t in n.targets));end=next(i for i,n in enumerate(tree.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='input_rows'for t in n.targets))
    modules={'display':ast.Module(body=tree.body[start:end],type_ignores=[]),'actual_file_validation':ast.Module(body=body,type_ignores=[])}
    return modules,{k:{'AST_SHA256':hashlib.sha256(ast.dump(v,include_attributes=False).encode()).hexdigest(),'lines':[min(n.lineno for n in v.body),max(n.end_lineno for n in v.body)],'original_nodes_unmodified':True}for k,v in modules.items()}
def validate(case,cw,co,secret,row):
    root=Path.cwd();d=root/'research/hdr-native';modules,binding=selected_modules((d/'run_hdr_s89.py').read_text());node=next(n for n in ast.parse((d/'carrier_case_s87.py').read_text()).body if isinstance(n,ast.ClassDef)and n.name=='ErrorState')
    scope=dict(globals(),R=root,D=d,case=case,cw=cw,co=co,secret=secret,row=row,node=node)
    exec(compile(modules['display'],'S89-original-display-settings','exec'),scope)
    exec(compile(modules['actual_file_validation'],'S89-original-actual-file-validation','exec'),scope)
    # The old validation marks its part complete; the outer delivery controller
    # independently completes only after all files and encryption are verified.
    row['completed']=False;row['S89_validation_AST_binding']=binding
    return {'AST_binding':binding,'headrooms':row['ideal_headroom_metrics'],'same_original_pixel_math':True}
