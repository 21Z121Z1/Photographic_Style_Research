"""S69 corrects only S68 host-call ABI; preserves failed parent evidence."""
from pathlib import Path
import hashlib,json,os
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out'
s=(D/'probe_bindings_s68.m').read_text()
old='Method prep=Signature(metal,NO,@"prepareToProcess:","i",@[@"i"]);int status=((int(*)(id,SEL,int))objc_msgSend)(renderer,method_getName(prep),1);'
new='Method prep=class_getInstanceMethod(metal,NSSelectorFromString(@"prepareToProcess:"));Need(prep!=NULL,@"prepare method");NSMethodSignature*ps=[NSMethodSignature signatureWithObjCTypes:method_getTypeEncoding(prep)];Need(ps.numberOfArguments==3&&strcmp(ps.methodReturnType,"i")==0,@"prepare return ABI");out[@"prepare_ABI"]=@(method_getTypeEncoding(prep));NSInvocation*pi=[NSInvocation invocationWithMethodSignature:ps];pi.target=renderer;pi.selector=method_getName(prep);const char*pt=[ps getArgumentTypeAtIndex:2];if(strcmp(pt,@encode(NSUInteger))==0){NSUInteger type=1;[pi setArgument:&type atIndex:2];}else if(strcmp(pt,"i")==0){int type=1;[pi setArgument:&type atIndex:2];}else if(strcmp(pt,"I")==0){unsigned type=1;[pi setArgument:&type atIndex:2];}else Need(NO,@"unknown prepare argument ABI");[pi invoke];int status=0;[pi getReturnValue:&status];'
assert s.count(old)==1;s=s.replace(old,new)
# Preserve nonzero ROI validation as a failed condition; collect both independent CPU contexts.
a='Need(r==0,@"original stats ROI check");';assert s.count(a)==1;s=s.replace(a,'/* nonzero recorded, never certified */')
a='@"check_status":@(r)}mutableCopy]';assert s.count(a)==1;s=s.replace(a,'@"check_status":@(r),@"renderer_class":NSStringFromClass([m class]),@"ROI_check_ABI":@(method_getTypeEncoding(check)),@"ROI_check_IMP_unslid":Hex(IMPAddress(check)-slide)}mutableCopy]')
a='@"inputLinearImageTextureMappedRegion"]';assert s.count(a)==1;s=s.replace(a,'@"inputLinearImageTextureMappedRegion",@"outputImageTextureMappedRegion",@"inputPersonMaskTextureMappedRegion",@"inputSkinMaskTextureMappedRegion",@"inputSkyMaskTextureMappedRegion",@"logicalImageToInputSkinMaskScale",@"logicalImageToInputSkyMaskScale"]')
a='[bindings addObject:b];';assert s.count(a)==1;s=s.replace(a,'b[@"wrapper_person_crop"]=[[wrapper valueForKey:@"inputPersonMaskCropRect"]description];'+a)
a='out[@"completed"]=@YES;';assert s.count(a)==1;s=s.replace(a,'BOOL valid=YES;for(NSDictionary*b in bindings)valid=valid&&[b[@"check_status"]intValue]==0;out[@"original_stats_ROI_checks_passed"]=@(valid);'+a)
# S69b + original assertion 0x2334d68e4: output is mandatory for the nonempty input/output intersection.
a='main=PB(w,h,NO),linear=';assert s.count(a)==1;s=s.replace(a,'main=PB(w,h,NO),output=PB(w,h,NO),linear=')
a='SetPB(wrapper,@"setInputPixelBuffer:",main);';assert s.count(a)==1;s=s.replace(a,a+'SetPB(wrapper,@"setOutputPixelBuffer:",output);')
a='CVPixelBufferRelease(main);';assert s.count(a)==1;s=s.replace(a,a+'CVPixelBufferRelease(output);')
target=W/'probe-s69.m';target.write_text(s)
(O/'derivation-s69.json').write_text(json.dumps({'parent':'probe_bindings_s68.m','parent_sha256':hashlib.sha256((D/'probe_bindings_s68.m').read_bytes()).hexdigest(),'derived_sha256':hashlib.sha256(s.encode()).hexdigest(),'only_change':'Exact prepare ABI and missing mandatory same-size output buffer; record all nonzero ROI checks; capture CPU bindings only, no image operator math changes','S68_failure_run':39338027870,'S68_ZIP_sha256':'d201b6cacef83c5bbc7ba922f82fba84008e06f94d5e5c801630ecfa95109ce5'},separators=(',',':'))+'\n')
body=(D/'run_hdr_s68.py').read_text();body=body.replace("str(D/'probe_bindings_s68.m'),'-o'","str(target),'-o'").replace("D/'run_hdr_s68.py'","D/'run_hdr_s69.py'")
exec(compile(body,'run_hdr_s68_derived_for_s69.py','exec'))
