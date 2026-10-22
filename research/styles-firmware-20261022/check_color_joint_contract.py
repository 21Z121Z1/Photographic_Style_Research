"""Check AIR10 neutral smoothSat/core precision and caller392 before reuse."""
import argparse,hashlib,json,re
from pathlib import Path
from native_semantic_tone_check import fragment
from color_matrices import TO_LMS_COLUMNS,TO_LAB_COLUMNS,FROM_LAB_A,FROM_LAB_B,FROM_ROOT_COLUMNS,POWER_HEX,INVERSE_POWER_HEX


def check(source,output):
    if output.exists():raise FileExistsError(output)
    text=source.read_text();fragment(text);functions=[m[0]for m in re.finditer(r'^define[^\n]*@[^\n]+\{\n.*?^}',text,re.M|re.S)];smooth=next(b for b in functions if '_Z15smoothSatFilter'in b.splitlines()[0]);main=next(b for b in functions if '@renderFinalAdjustments('in b.splitlines()[0]);whites=next(b for b in functions if '_Z11whitesCurve'in b.splitlines()[0]);rows=[]
    expected={6:TO_LMS_COLUMNS[0],8:TO_LMS_COLUMNS[1],11:TO_LMS_COLUMNS[2],15:(POWER_HEX,),18:TO_LAB_COLUMNS[0],20:TO_LAB_COLUMNS[1],23:TO_LAB_COLUMNS[2],51:FROM_LAB_A,54:FROM_LAB_B,58:(INVERSE_POWER_HEX,),61:FROM_ROOT_COLUMNS[0],63:FROM_ROOT_COLUMNS[1],66:FROM_ROOT_COLUMNS[2]}
    for ssa,wanted in expected.items():
        line=next(l for l in smooth.splitlines()if l.startswith(f'  %{ssa} ='));rows.append({'SSA':ssa,'literal_match':tuple(re.findall(r'0x([0-9A-F]{16})',line))==wanted,'f32_operation':'float'in line,'instruction_sha256':hashlib.sha256(line.encode()).hexdigest()})
    patterns={'Lab_half25':'%25 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32','dot_half36':'%36 = tail call fast half @air.dot.v2f16','sqrt_half37':'%37 = tail call fast half @air.sqrt.f16','radius_gain_half41':'%41 = fmul fast half %37, %1','cos_half42':'%42 = tail call fast half @air.cos.f16','sin_half45':'%45 = tail call fast half @air.sin.f16','inverse_half_input48':'%48 = tail call fast <3 x float> @air.convert.f.v3f32.f.v3f16','converted_half68':'%68 = tail call fast <3 x half> @air.convert.f.v3f16.f.v3f32','original_clamp69':'%69 = tail call fast <3 x half> @air.saturate.v3f16','original_final_half71':'%71 = fadd fast <3 x half> %70, %69','gain_branch_f3273':'%73 = fcmp fast olt float %72, 0x3F947AE140000000'}
    checks={k:v in smooth for k,v in patterns.items()};caller={'zero_color_square_half361':'%361 = fmul fast half %357, %357'in main,'gain_half364':'%364 = fadd fast half %363, 0xH3C00'in main,'mix_half392':'%392 = tail call fast <3 x half> @air.mix.v3f16'in main,'smooth_gain364':bool(re.search(r'%372 = .*@_Z15smoothSatFilter[^\n]*half noundef %364',main))};whites_order={'product_half42':'%42 = fmul fast <3 x half> %41, %14'in whites,'division_half45':'%45 = fdiv fast <3 x half> %42, %44'in whites,'index_half22':'%22 = fmul fast half %21, %18'in whites}
    result={'scope':__doc__,'reference':'iPhone17,3 /24A446 AIR10','smooth_function_sha256':hashlib.sha256(smooth.encode()).hexdigest(),'smooth_source_line':text.count('\n',0,text.index(smooth))+1,'main_function_sha256':hashlib.sha256(main.encode()).hexdigest(),'whites_function_sha256':hashlib.sha256(whites.encode()).hexdigest(),'constant_rows':rows,'precision_checks':checks,'caller_checks':caller,'whites_order_checks':whites_order,'all_match':all(r['literal_match']and r['f32_operation']for r in rows)and all(checks.values())and all(caller.values())and all(whites_order.values()),'reuse_condition':'set backend; exact raw color3 zero -> actual half gain1; gray-gain branch false; original exterior and clamp retained','native_calls':0,'original_GPU_verified':False};output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'all_match':result['all_match'],'smooth_function_sha256':result['smooth_function_sha256']}))
    if not result['all_match']:raise AssertionError('Precision/caller contract mismatch')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.source,a.output)
