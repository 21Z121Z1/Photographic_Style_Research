"""Text-only MSL contract inventory. Run local Python under the memory scope.

The PDF is an external reference, not uploaded or bundled. This extractor
records facts/page references, not the specification's full text.
"""
import argparse,hashlib,json,logging,re,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('pdf',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--parser-dir',type=Path);a=ap.parse_args()
if a.parser_dir:sys.path.insert(0,str(a.parser_dir))
logging.getLogger('pypdf').setLevel(logging.ERROR)
from pypdf import PdfReader,__version__
EXPECTED='41538b30d2f1140a5b2a0c84ce0a9f7b67bf0c707e224cfea0bfe5a44aa26cf5'
with a.pdf.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
assert actual==EXPECTED,'Reference PDF changed; re-review contracts, do not silently accept a new revision'
r=PdfReader(a.pdf);pages={n:r.pages[n-1].extract_text() for n in [1,15,16,205,208,368,370,371,372,373,374,375,376,378,379]}
assert len(r.pages)==383 and 'Version 4.1' in pages[1]
half=pages[373].split('Table 8.3. Accuracy',1)[1]+'\n'+pages[374].split('Table 8.4 describes',1)[0]
assert re.search(r'atan2\(y, x\)\s+<= 1 ulp',half)
assert 'T pow(T x, T y)' in pages[208] and 'T powr(T x, T y)' in pages[208]
assert not re.search(r'\bpowr?\b',half)
facts={
 'half_atan2_max_ulp':1,'half_atan2_pages':[373,374],
 'half_table_hardware_condition':'Apple GPU Family4 or later (reported device support checked separately)',
 'half_pow_or_powr_numeric_row_in_Table8_3':False,
 'pow_half_overload_exists_in_Table6_4':True,
 'explicit_fast_precise_namespaces_described_for':'single precision only',
 'fp32_fast_pow_description':'exp2(y*log2(x)); apply log2/exp2 bounds and domain conditions, not one constant ULP for the whole shader',
 'fp32_fast_pow_pages':[371,372],'half_pow_reviewed_pages':[205,208,373,374],
 'arithmetic_rounding_allowed':['ties-to-even','toward-zero'],
 'arithmetic_subnormal_FTZ_allowed':True,
 'float_to_half_conversion':'ties-to-even; generated half subnormals not flushed by this conversion',
 'half_to_float_conversion':'lossless',
 'fast_reassociation_and_contraction_allowed':True,
 'fast_nonfinite_handling':'undefined; a zero divisor can invalidate a fast program',
 'texture_coordinates_must_be_finite':True,
 'per_primitive_ULP_is_not_whole_program_error_contract':True,
 'scope':'These are checked language-level facts, not a certified implementation of AIR intrinsics or a global inverse bound.'}
assert 'exp2(y * log2(x))' in pages[372] and 'No NaNs' in pages[15] and 'Allow Reassociation' in pages[15]
assert 'If Y can be zero' in pages[16] and 'reassociate floating-point operations' in pages[375]
result={'source':{'url':'https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf','sha256':actual,'size_bytes':a.pdf.stat().st_size,'version':'4.1','publication_date':'2026-06-04','pdf_pages':383},'parser':{'package':'pypdf','version':__version__,'page_text_only':True,'full_pdf_or_sections_uploaded':False},'facts':facts,'missing_conditions':['A bounded half pow/powr implementation or a proof eliminating every relevant occurrence','An enclosure of the actual lowered program/allowed rewrites','All feasible F and F0 paths satisfy domain safety, including finite sample coordinates','Sound texture footprint/value enclosure and whole declared-domain coverage'],'original_gates_changed':False}
with a.output.open('x') as f:f.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'source_sha256':actual,'half_pow_numeric_row':False,'whole_consumer_certified':False}))
