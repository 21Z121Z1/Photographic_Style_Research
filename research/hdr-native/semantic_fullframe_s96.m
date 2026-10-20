// S94: full original-size native semantic references and bounded patch replay.
// No inverse, new Apple shader, mathematical approximation or sampler override.
#define main FrozenFilterMain
#include "native_filter_probe_s96.m"
#undef main
#import <CommonCrypto/CommonDigest.h>
#import <mach-o/dyld.h>
#import <mach-o/loader.h>
#include "encoder_capture_s96.inc"
#include "replay_helpers_v7.inc"
@interface NSObject (SemanticS94)
- (id<MTLCommandQueue>)metalCommandQueue;
- (int)finishProcessing;
@end
static NSString *Root94;
static NSMutableArray *Calls94;
static NSMutableArray *Processes94;
static int (*Old94)(id,SEL);
static NSUInteger Serial94;
static NSUInteger PixelsAccepted96;
static void Need94(BOOL ok,NSString *reason){if(!ok)@throw[NSException exceptionWithName:@"S94Contract"reason:reason userInfo:nil];}
static BOOL NoResidency94(id s,SEL c){return NO;}
static NSString *Hex94(const unsigned char*b,NSUInteger n){NSMutableString*s=[NSMutableString new];for(NSUInteger i=0;i<n;i++)[s appendFormat:@"%02x",b[i]];return s;}
static NSString *Hash94(NSData*d){unsigned char b[CC_SHA256_DIGEST_LENGTH];CC_SHA256(d.bytes,(CC_LONG)d.length,b);return Hex94(b,sizeof(b));}
static void JSON94(id o,NSString*p){NSError*e=nil;NSData*d=[NSJSONSerialization dataWithJSONObject:o options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:&e];Need94(d!=nil,e.description?:@"JSON");Need94([d writeToFile:p options:0 error:&e],e.description?:@"write JSON");}
static NSUInteger BPP94(MTLPixelFormat f){switch(f){case MTLPixelFormatR8Unorm:return 1;case MTLPixelFormatR16Float:return 2;case MTLPixelFormatR32Float:case MTLPixelFormatRG16Float:return 4;case MTLPixelFormatRG32Float:case MTLPixelFormatRGBA16Float:return 8;case MTLPixelFormatRGBA32Float:return 16;default:return 0;}}
static NSData*Region94(id<MTLCommandQueue>q,id<MTLTexture>t,NSUInteger x,NSUInteger y,NSUInteger w,NSUInteger h){
 NSUInteger b=BPP94(t.pixelFormat);Need94(b&&x+w<=t.width&&y+h<=t.height,@"readable texture format/region");NSUInteger row=(w*b+255)&~255;
 id<MTLBuffer>buf=[q.device newBufferWithLength:row*h options:MTLResourceStorageModeShared];Need94(buf!=nil,@"region buffer allocation");id<MTLCommandBuffer>cb=[q commandBuffer];id<MTLBlitCommandEncoder>blit=[cb blitCommandEncoder];
 [blit copyFromTexture:t sourceSlice:0 sourceLevel:0 sourceOrigin:MTLOriginMake(x,y,0)sourceSize:MTLSizeMake(w,h,1)toBuffer:buf destinationOffset:0 destinationBytesPerRow:row destinationBytesPerImage:row*h];[blit endEncoding];[cb commit];[cb waitUntilCompleted];Need94(!cb.error,cb.error.description?:@"texture read");
 NSMutableData*d=[NSMutableData dataWithLength:w*h*b];for(NSUInteger j=0;j<h;j++)memcpy((char*)d.mutableBytes+j*w*b,(char*)buf.contents+j*row,w*b);return d;
}
static NSString*TextureHash94(id<MTLCommandQueue>q,id<MTLTexture>t){CC_SHA256_CTX c;CC_SHA256_Init(&c);for(NSUInteger y=0;y<t.height;y+=64){@autoreleasepool{NSData*d=Region94(q,t,0,y,t.width,MIN((NSUInteger)64,t.height-y));CC_SHA256_Update(&c,d.bytes,(CC_LONG)d.length);}}unsigned char h[32];CC_SHA256_Final(h,&c);return Hex94(h,32);}
static NSArray*Images94(void){NSMutableArray*a=[NSMutableArray new];for(uint32_t i=0;i<_dyld_image_count();i++){const char*p=_dyld_get_image_name(i);if(!p||(!strstr(p,"/CMImaging.framework/")&&!strstr(p,"/PhotoImaging.framework/")))continue;const struct mach_header_64*m=(const void*)_dyld_get_image_header(i);if(m->magic!=MH_MAGIC_64)continue;const struct load_command*l=(const void*)(m+1);NSString*u=@"missing";for(uint32_t j=0;j<m->ncmds;j++){if(l->cmd==LC_UUID){const struct uuid_command*v=(const void*)l;u=[[NSUUID alloc]initWithUUIDBytes:v->uuid].UUIDString;}l=(const void*)((const char*)l+l->cmdsize);}[a addObject:@{@"path":@(p),@"loaded_UUID":u}];}return a;}
static NSDictionary*Metrics94(NSData*a,NSData*b){Need94(a.length==b.length&&a.length%8==0,@"metric RGBA16 shape");const __fp16*x=a.bytes,*y=b.bytes;double maximum=0,sq=0,relative=0;uint64_t bits=0,nf=0;NSUInteger n=a.length/8;
 for(NSUInteger i=0;i<n;i++)for(int c=0;c<3;c++){NSUInteger k=i*4+c;bits+=memcmp(x+k,y+k,2)!=0;if(!isfinite((float)x[k])||!isfinite((float)y[k])){nf++;continue;}double d=fabs((double)x[k]-y[k]);maximum=fmax(maximum,d);relative=fmax(relative,d/fmax(fabs((double)y[k]),1e-6));sq+=d*d;}
 return @{@"pixels":@(n),@"half_differing_components":@(bits),@"nonfinite_components":@(nf),@"max_abs":@(maximum),@"max_relative_all_RGB_denominator_1e6":@(relative),@"SSE_RGB":@(sq),@"PSNR_peak1_dB":sq?@(-10*log10(sq/(n*3))):@"inf"};}
static NSDictionary*Params94(NSDictionary*snap,NSArray*fields,NSMutableDictionary*proof){NSMutableData*d=[snap[@"1"]mutableCopy];Need94(d.length==672,@"params672");NSData*before=[d copy];NSMutableIndexSet*allowed=[NSMutableIndexSet new];NSMutableArray*changes=[NSMutableArray new];for(NSNumber*f in fields){NSUInteger off=556+4*f.unsignedIntegerValue;float v=0;memcpy(&v,(const char*)d.bytes+off,4);[changes addObject:@{@"field":f,@"offset":@(off),@"before":@(v),@"after":@0}];memset((char*)d.mutableBytes+off,0,4);[allowed addIndexesInRange:NSMakeRange(off,4)];}NSUInteger outside=0;for(NSUInteger i=0;i<d.length;i++)if(![allowed containsIndex:i]&&((const char*)d.bytes)[i]!=((const char*)before.bytes)[i])outside++;proof[@"changed_bytes_outside_target"]=@(outside);proof[@"changes"]=changes;proof[@"params_before_SHA256"]=Hash94(before);proof[@"params_after_SHA256"]=Hash94(d);NSMutableDictionary*s=[snap mutableCopy];s[@"1"]=d;return s;}
static NSDictionary*Patch94(NSDictionary*call,id<MTLDevice>dev,NSUInteger x,NSUInteger y,NSUInteger w,NSUInteger h){
 NSData*original=call[@"bytes"][@"5"];Need94(original.length==176,@"SSRRenderROI176 bytes binding");NSMutableData*r=[original mutableCopy];
 // AIR buffer5+16..144: nine float4(sx,sy,tx,ty) normalized samplings.
 // Keep every original texture and its dimensions. Only relocate the patch gid.
 for(NSUInteger off=16;off<=144;off+=16){float m[4];memcpy(m,(const char*)r.bytes+off,16);m[2]=fmaf((float)x,m[0],m[2]);m[3]=fmaf((float)y,m[1],m[3]);memcpy((char*)r.mutableBytes+off,m,16);}
 uint16_t shape[2]={(uint16_t)w,(uint16_t)h},origin[2]={0,0};memcpy((char*)r.mutableBytes+8,shape,4);memcpy((char*)r.mutableBytes+160,origin,4);
 id<MTLTexture>ref=call[@"textures"][@"13"];MTLTextureDescriptor*td=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:ref.pixelFormat width:w height:h mipmapped:NO];td.storageMode=MTLStorageModePrivate;td.usage=MTLTextureUsageShaderRead|MTLTextureUsageShaderWrite;id<MTLTexture>placeholder=[dev newTextureWithDescriptor:td];Need94(placeholder!=nil,@"patch output allocation");
 NSMutableDictionary*c=[call mutableCopy],*b=[call[@"bytes"]mutableCopy],*t=[call[@"textures"]mutableCopy];b[@"5"]=r;t[@"13"]=placeholder;c[@"bytes"]=b;c[@"textures"]=t;c[@"dispatch"]=@"threads";c[@"grid"]=@[@(w),@(h),@1];return c;
}
static void Store94(NSData*d,NSString*dir,NSString*name,NSUInteger w,NSUInteger h){NSString*p=[dir stringByAppendingPathComponent:name];Need94(![[NSFileManager defaultManager]fileExistsAtPath:p],@"exclusive output");Need94([d writeToFile:p atomically:NO],@"write pixels");JSON94(@{@"shape":@[@(h),@(w),@4],@"dtype":@"<f2",@"sha256":Hash94(d),@"space":@"Captured kernel space; native CI P3 comparison required"},[p stringByAppendingString:@".json"]);}
#include "observer_prerequisites_s96.inc"
static NSDictionary*Probe94(id renderer,NSDictionary*call,NSString*dir){
 id<MTLCommandQueue>q=[renderer metalCommandQueue];id<MTLTexture>ot=call[@"textures"][@"13"];id<MTLComputePipelineState>ps=call[@"pipeline_object"];NSDictionary*snap=V2BufferSnapshots(call,q);NSMutableDictionary*row=[@{@"output_shape":@[@(ot.height),@(ot.width)],@"source_shape":@[@(((id<MTLTexture>)call[@"textures"][@"0"]).height),@(((id<MTLTexture>)call[@"textures"][@"0"]).width)],@"grid":call[@"grid"],@"group":call[@"group"],@"dispatch":call[@"dispatch"],@"loaded_images":Images94(),@"retained_native_pipeline":ps.description?:@"nil",@"no_recompiled_Apple_shader":@YES,@"region_reference_available":@NO}mutableCopy];
 NSDictionary*owner=[NSThread currentThread].threadDictionary[OwnerKey96];row[@"CI_owner"]=owner?:@{};
 NSArray*rect=owner[@"output_region"];BOOL ownerOK=rect.count==4;double coords[4]={0};if(ownerOK)for(int j=0;j<4;j++){if(![rect[j]isKindOfClass:NSNumber.class]){ownerOK=NO;break;}coords[j]=[rect[j]doubleValue];ownerOK&=isfinite(coords[j])&&fabs(coords[j]-round(coords[j]))<1e-6;}ownerOK&=coords[0]>=0&&coords[1]>=0&&coords[2]>0&&coords[3]>0&&coords[0]+coords[2]<=5712&&coords[1]+coords[3]<=4284;
 NSData*roi=call[@"bytes"][@"5"];uint16_t origin[2]={UINT16_MAX,UINT16_MAX};if(roi.length==176)memcpy(origin,(const char*)roi.bytes+160,4);row[@"output_origin_u16"]=@[@(origin[0]),@(origin[1])];
 if(!ownerOK||ot.width!=(NSUInteger)coords[2]||ot.height!=(NSUInteger)coords[3]||ot.pixelFormat!=MTLPixelFormatRGBA16Float||roi.length!=176||origin[0]||origin[1]||call[@"textures"][@"14"]){row[@"stop_reason"]=@"Owner/physical-output/ROI geometry unproven or second write target present; census only, unknown padding is not serialized";JSON94(row,[dir stringByAppendingPathComponent:@"native.json"]);return row;}
 BOOL budget=NO;@synchronized(Calls94){budget=PixelsAccepted96+ot.width*ot.height<=24470208;if(budget)PixelsAccepted96+=ot.width*ot.height;}if(!budget){row[@"stop_reason"]=@"Reference pixel budget already consumed; no duplicate full-photo allocation";JSON94(row,[dir stringByAppendingPathComponent:@"native.json"]);return row;}
 NSMutableDictionary*hashes=[NSMutableDictionary new];for(NSString*k in call[@"textures"]){@autoreleasepool{id<MTLTexture>t=call[@"textures"][k];Need94(BPP94(t.pixelFormat)>0,@"known readable native texture format");hashes[k]=@{@"width":@(t.width),@"height":@(t.height),@"format":@(t.pixelFormat),@"SHA256":TextureHash94(q,t)};}}row[@"bindings_before"]=hashes;
 // Only established initialized ABI payload sizes are serialized; other
 // captured allocations get hashes, never raw padding.
 for(NSString*k in @[@"1",@"3"]){NSData*d=snap[k];NSUInteger expected=[k isEqualToString:@"1"]?672:10640;Need94(d.length==expected,@"original known uniform ABI length");[d writeToFile:[dir stringByAppendingPathComponent:[NSString stringWithFormat:@"buffer-%@.bin",k]]atomically:NO];}
 for(NSString*k in @[@"0",@"5"]){NSData*d=call[@"bytes"][k];NSUInteger expected=[k isEqualToString:@"0"]?320:176;if(d.length==expected)[d writeToFile:[dir stringByAppendingPathComponent:[NSString stringWithFormat:@"bytes-%@.bin",k]]atomically:NO];}
 row[@"region_reference_available"]=@YES;NSData*ref=Region94(q,ot,0,0,ot.width,ot.height);Store94(ref,dir,@"native.f16",ot.width,ot.height);
 @autoreleasepool{NSData*control=V2Evaluate(q,call,snap,ps,nil,nil);row[@"native_hydration"]=Metrics94(control,ref);Need94([row[@"native_hydration"][@"half_differing_components"]unsignedLongLongValue]==0,@"original PSO hydration zero");}
 NSMutableArray*trials=[NSMutableArray new];NSArray*specs=@[@[@"original",@[]],@[@"skin-color",@[@9]],@[@"skin-brightness",@[@10]],@[@"skin-both",@[@9,@10]]];
 for(NSArray*spec in specs){@autoreleasepool{
  NSString*name=spec[0];NSMutableDictionary*trial=[@{@"operator":name}mutableCopy];NSDictionary*state=Params94(snap,spec[1],trial);NSData*whole=[name isEqualToString:@"original"]?ref:V2Evaluate(q,call,state,ps,nil,nil);Need94([trial[@"changed_bytes_outside_target"]unsignedIntegerValue]==0,@"target only parameter control");trial[@"difference_from_original"]=Metrics94(whole,ref);
  if(![name isEqualToString:@"original"])Store94(whole,dir,[name stringByAppendingString:@".f16"],ot.width,ot.height);
  NSString*tilepath=[dir stringByAppendingPathComponent:[name stringByAppendingString:@"-stitched.f16"]];Need94([[NSFileManager defaultManager]createFileAtPath:tilepath contents:nil attributes:nil],@"new stitched output");NSFileHandle*out=[NSFileHandle fileHandleForWritingAtPath:tilepath];[out truncateFileAtOffset:whole.length];
  NSMutableArray*patches=[NSMutableArray new];uint64_t pixels=0,bits=0,nf=0;double mx=0,sse=0;for(NSUInteger y=0;y<ot.height;y+=384)for(NSUInteger x=0;x<ot.width;x+=512){@autoreleasepool{
   NSUInteger w=MIN((NSUInteger)512,ot.width-x),h=MIN((NSUInteger)384,ot.height-y);NSDictionary*c=Patch94(call,q.device,x,y,w,h);NSData*t=V2Evaluate(q,c,state,ps,nil,nil);NSMutableData*cut=[NSMutableData dataWithLength:w*h*8];for(NSUInteger j=0;j<h;j++){memcpy((char*)cut.mutableBytes+j*w*8,(const char*)whole.bytes+((y+j)*ot.width+x)*8,w*8);[out seekToFileOffset:((y+j)*ot.width+x)*8];[out writeData:[t subdataWithRange:NSMakeRange(j*w*8,w*8)]];}NSDictionary*m=Metrics94(t,cut);[patches addObject:@{@"xywh":@[@(x),@(y),@(w),@(h)],@"metrics":m,@"patch_SHA256":Hash94(t),@"reference_crop_SHA256":Hash94(cut)}];pixels+=w*h;bits+=[m[@"half_differing_components"]unsignedLongLongValue];nf+=[m[@"nonfinite_components"]unsignedLongLongValue];mx=fmax(mx,[m[@"max_abs"]doubleValue]);sse+=[m[@"SSE_RGB"]doubleValue];
  }}[out synchronizeFile];[out closeFile];Need94(pixels==ot.width*ot.height,@"all original pixels covered once");trial[@"patches"]=patches;trial[@"patch_pixels"]=@(pixels);trial[@"patch_count"]=@(patches.count);trial[@"tile_half_differing_components"]=@(bits);trial[@"tile_nonfinite_components"]=@(nf);trial[@"tile_max_abs"]=@(mx);trial[@"tile_PSNR_peak1_dB"]=sse?@(-10*log10(sse/(pixels*3))):@"inf";[trials addObject:trial];row[@"trials"]=trials;JSON94(row,[dir stringByAppendingPathComponent:@"native-checkpoint.json"]);
 }}
 NSMutableDictionary*after=[NSMutableDictionary new];BOOL same=YES;for(NSString*k in hashes){@autoreleasepool{NSString*h=TextureHash94(q,call[@"textures"][k]);after[k]=h;same&=[h isEqualToString:hashes[k][@"SHA256"]];}}NSDictionary*current=V2BufferSnapshots(call,q);for(NSString*k in snap)same&=[snap[k]isEqual:current[k]];row[@"bindings_after_SHA256"]=after;row[@"all_original_textures_and_buffers_unchanged"]=@(same);Need94(same,@"original context immutable");JSON94(row,[dir stringByAppendingPathComponent:@"native.json"]);return row;
}
static int Process94(id s,SEL c){@autoreleasepool{
 Need94([[NSFileManager defaultManager]createDirectoryAtPath:Root94 withIntermediateDirectories:YES attributes:nil error:NULL],@"capture directory");
 __attribute__((objc_precise_lifetime)) NSMutableDictionary*states=[NSMutableDictionary new];
 __attribute__((objc_precise_lifetime)) NSMutableArray*dispatches=[NSMutableArray new];
 ECStates=states;ECDispatches=dispatches;NSMutableDictionary*td=[NSThread currentThread].threadDictionary;id oldGuided=td[GuidedKey96];NSMutableArray*guided=[NSMutableArray new];td[GuidedKey96]=guided;
 NSUInteger serial;@synchronized(Calls94){serial=Serial94++;}uint64_t tid=0;pthread_threadid_np(NULL,&tid);NSDictionary*allocation=Allocator96(s);NSDictionary*owner=[td[OwnerKey96]copy]?:@{};
 ECActive=YES;int rc=Old94(s,c);[s finishProcessing];ECActive=NO;
 @try{if(rc==0){NSMutableArray*matches=[NSMutableArray new];for(NSDictionary*d in dispatches)if(d[@"textures"][@"13"]&&d[@"textures"][@"11"]&&d[@"buffers"][@"1"])[matches addObject:d];
  if(matches.count==1){NSString*folder=[Root94 stringByAppendingPathComponent:[NSString stringWithFormat:@"dispatch-%lu",(unsigned long)serial]];Need94([[NSFileManager defaultManager]createDirectoryAtPath:folder withIntermediateDirectories:YES attributes:nil error:NULL],@"native capture directory");NSMutableDictionary*row=[Probe94(s,matches[0],folder)mutableCopy];row[@"serial"]=@(serial);@synchronized(Calls94){[Calls94 addObject:row];}}
  else if(matches.count>1){@synchronized(Calls94){[Calls94 addObject:@{@"serial":@(serial),@"stop_reason":@"More than one candidate final dispatch in one owner callback; census only"}];}}
 }}@catch(NSException*e){@synchronized(Calls94){[Calls94 addObject:@{@"serial":@(serial),@"exception":e.reason?:e.name}];}}
 NSMutableArray*census=[NSMutableArray new];NSArray*observed=dispatches.count?dispatches:states.allValues;
 for(NSDictionary*d in observed){NSMutableDictionary*t=[NSMutableDictionary new];for(NSString*k in d[@"textures"]){id<MTLTexture>v=d[@"textures"][k];t[k]=Tex96(v);}id<MTLComputePipelineState>ps=d[@"pipeline_object"];[census addObject:@{@"textures":t,@"buffer_keys":[d[@"buffers"]allKeys]?:@[],@"byte_keys":[d[@"bytes"]allKeys]?:@[],@"grid":d[@"grid"]?:@[],@"group":d[@"group"]?:@[],@"pipeline_description":ps.description?:@"nil"}];}
 @synchronized(Calls94){[Processes94 addObject:@{@"serial":@(serial),@"thread_id":@(tid),@"renderer_id":[NSString stringWithFormat:@"%p",s],@"CI_owner":owner,@"allocator_before_process":allocation,@"original_process_return":@(rc),@"guided_calls":guided,@"dispatch_record_count":@(dispatches.count),@"encoder_state_count":@(states.count),@"census_is_bound_state_fallback_not_actual_dispatch":@(dispatches.count==0),@"captured_dispatches_or_states":census}];
 JSON94(@{@"calls":[Calls94 copy],@"processes":[Processes94 copy],@"pool_events":[PoolEvents96 copy],@"runtime":Runtime96,@"scope":@"One original5712x4284 CI request; native owner regions must cover every pixel once. Forward controls only, not baked-camera inverse."},[Root94 stringByAppendingPathComponent:@"native-calls.json"]);}
 if(oldGuided)td[GuidedKey96]=oldGuided;else[td removeObjectForKey:GuidedKey96];ECStates=nil;ECDispatches=nil;return rc;
}}
int main(int argc,char**argv){@autoreleasepool{if(argc!=4)return 2;Root94=[@(argv[3])stringByAppendingPathComponent:@"semantic-full"];Calls94=[NSMutableArray new];Processes94=[NSMutableArray new];
 dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",RTLD_NOW|RTLD_LOCAL);Method m=class_getClassMethod(NSClassFromString(@"CMIMetalResourceCache"),NSSelectorFromString(@"_enableResidencySets"));if(m)method_setImplementation(m,(IMP)NoResidency94);
 dlopen("/System/Library/PrivateFrameworks/NeutrinoCore.framework/NeutrinoCore",RTLD_NOW|RTLD_LOCAL);dlopen("/System/Library/PrivateFrameworks/PhotoImaging.framework/PhotoImaging",RTLD_NOW|RTLD_LOCAL);
 InstallPrerequisites96();ECInstall();m=class_getInstanceMethod(NSClassFromString(@"CMISmartStyleMetalRendererV1"),NSSelectorFromString(@"process"));Need94(m!=NULL,@"native renderer process");Old94=(void*)method_getImplementation(m);method_setImplementation(m,(IMP)Process94);return FrozenFilterMain(argc,argv);
}}
