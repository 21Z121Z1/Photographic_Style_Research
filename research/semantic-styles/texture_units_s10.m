#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <CommonCrypto/CommonDigest.h>
static const NSUInteger W=512,H=384,N=512*384;
static NSString*Sha(NSData*d){unsigned char a[32];CC_SHA256(d.bytes,(CC_LONG)d.length,a);NSMutableString*s=[NSMutableString new];for(int k=0;k<32;k++)[s appendFormat:@"%02x",a[k]];return s;}
static void Put(id o,NSString*p){[[NSJSONSerialization dataWithJSONObject:o options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL]writeToFile:p atomically:YES];}
static id<MTLTexture>Tex(id<MTLDevice>d,MTLPixelFormat fmt,NSData*a){MTLTextureDescriptor*t=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:fmt width:W height:H mipmapped:NO];t.storageMode=MTLStorageModeShared;t.usage=MTLTextureUsageShaderRead|MTLTextureUsageShaderWrite;id<MTLTexture>x=[d newTextureWithDescriptor:t];if(a)[x replaceRegion:MTLRegionMake2D(0,0,W,H)mipmapLevel:0 withBytes:a.bytes bytesPerRow:a.length/H];return x;}
static NSData*Read(id<MTLTexture>t){NSMutableData*d=[NSMutableData dataWithLength:N*8];[t getBytes:d.mutableBytes bytesPerRow:W*8 fromRegion:MTLRegionMake2D(0,0,W,H)mipmapLevel:0];return d;}
int main(int argc,char**argv){@autoreleasepool{
 if(argc!=3)return 2;NSString*in=@(argv[1]),*out=@(argv[2]);[[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:YES attributes:nil error:NULL];id<MTLDevice>d=MTLCreateSystemDefaultDevice();id<MTLCommandQueue>q=[d newCommandQueue];NSError*err=nil;NSString*libpath=@"/System/Library/PrivateFrameworks/CMImaging.framework/Resources/default.metallib";id<MTLLibrary>lib=[d newLibraryWithFile:libpath error:&err];NSMutableArray*results=[NSMutableArray new];
 NSArray*names=@[@"original",@"blur",@"scaledblur",@"skin",@"person",@"precomputed",@"gfA",@"gfB",@"ones",@"zero"];
 NSMutableDictionary*tex=[NSMutableDictionary new],*facts=[NSMutableDictionary new];for(NSString*n in names){NSData*a=[NSData dataWithContentsOfFile:[in stringByAppendingPathComponent:[n stringByAppendingString:@".f16"]]];BOOL scalar=[@[@"skin",@"person",@"ones"]containsObject:n];if(a.length!=N*(scalar?2:8))return 3;tex[n]=Tex(d,scalar?MTLPixelFormatR16Float:MTLPixelFormatRGBA16Float,a);facts[n]=@{@"sha256":Sha(a),@"bytes":@(a.length)};}
 NSData*source=Read(tex[@"original"]);const __fp16*original=source.bytes;
 for(NSString*op in @[@"SkinSmooth",@"Mattify"]){@autoreleasepool{
 NSString*fname=[op isEqual:@"SkinSmooth"]?@"CMITextureStylesSkinSmoothenStandalone::finalBlendingKernelInPlace":@"CMITextureStylesMattify::ApplyRegionAddbackAndEditingStrength";
 MTLFunctionConstantValues*fc=[MTLFunctionConstantValues new];BOOL no=NO;[fc setConstantValue:&no type:MTLDataTypeBool atIndex:16];[fc setConstantValue:&no type:MTLDataTypeBool atIndex:0];id<MTLFunction>fn=[op isEqual:@"SkinSmooth"]?[lib newFunctionWithName:fname]:[lib newFunctionWithName:fname constantValues:fc error:&err];id<MTLComputePipelineState>ps=fn?[d newComputePipelineStateWithFunction:fn error:&err]:nil;
 if(!ps){[results addObject:@{@"operator":op,@"error":err.description?:@"missing pipeline"}];continue;}
 NSMutableDictionary*bindings=[@{@"imageblock_memory_16x16":@([ps imageblockMemoryLengthForDimensions:MTLSizeMake(16,16,1)]),@"max_threads":@(ps.maxTotalThreadsPerThreadgroup),@"uses_imageblock":@([op isEqual:@"SkinSmooth"]),@"explicit_thumbnail_function_constant_zero":@([op isEqual:@"Mattify"])}mutableCopy];
 NSData*(^eval)(NSData*,float)=^NSData*(NSData*a,float strength){
 id<MTLTexture>input=Tex(d,MTLPixelFormatRGBA16Float,a),output=Tex(d,MTLPixelFormatRGBA16Float,nil);id<MTLCommandBuffer>cb=[q commandBuffer];id<MTLComputeCommandEncoder>e=[cb computeCommandEncoder];[e setComputePipelineState:ps];[e setTexture:input atIndex:0];float roi[4]={0,0,1,1};uint16_t ort[6]={0,0,0,0,W,H};
 if([op isEqual:@"SkinSmooth"]){
  [e setImageblockWidth:16 height:16];[e setTexture:output atIndex:7];[e setTexture:tex[@"skin"]atIndex:1];[e setTexture:tex[@"ones"]atIndex:2];[e setTexture:tex[@"blur"]atIndex:3];[e setTexture:tex[@"ones"]atIndex:5];[e setTexture:tex[@"gfA"]atIndex:8];[e setTexture:tex[@"gfB"]atIndex:9];[e setTexture:tex[@"precomputed"]atIndex:10];[e setTexture:tex[@"person"]atIndex:11];[e setTexture:tex[@"zero"]atIndex:12];[e setTexture:tex[@"zero"]atIndex:13];
  uint8_t params[176]={0};((float*)params)[12]=.1f*strength;((float*)params)[13]=.2f*strength;params[166]=1;float stats[8]={.6f,.5f,.4f,1,.1f,0,0,0};id<MTLBuffer>b=[d newBufferWithBytes:stats length:sizeof(stats)options:MTLResourceStorageModeShared];[e setBuffer:b offset:0 atIndex:4];uint32_t size[2]={W,H};[e setBytes:size length:sizeof(size)atIndex:6];[e setBytes:ort length:sizeof(ort)atIndex:5];[e setBytes:params length:sizeof(params)atIndex:3];for(NSNumber*k in @[@1,@2,@7,@8,@9,@10,@11])[e setBytes:roi length:sizeof(roi)atIndex:k.unsignedIntegerValue];
  if(strength==1){bindings[@"params_sha256"]=Sha([NSData dataWithBytes:params length:sizeof(params)]);bindings[@"stats_sha256"]=Sha([NSData dataWithBytes:stats length:sizeof(stats)]);}
 }else{
  [e setTexture:output atIndex:1];[e setTexture:tex[@"ones"]atIndex:23];[e setTexture:tex[@"skin"]atIndex:27];[e setTexture:tex[@"blur"]atIndex:25];[e setTexture:tex[@"scaledblur"]atIndex:24];[e setTexture:tex[@"ones"]atIndex:19];float params[18]={.3f,.2f,1,.1f,-.1f,.1f,.25f,.05f,1,1,0,1,-.1f,.1f,0,180,0,1};float frac=.1f,average[4]={.6f,.5f,.4f,0};id<MTLBuffer>fb=[d newBufferWithBytes:&frac length:sizeof(frac)options:MTLResourceStorageModeShared],ab=[d newBufferWithBytes:average length:sizeof(average)options:MTLResourceStorageModeShared];[e setBuffer:fb offset:0 atIndex:22];[e setBuffer:ab offset:0 atIndex:17];[e setBytes:&strength length:4 atIndex:21];[e setBytes:params length:sizeof(params)atIndex:25];[e setBytes:ort length:sizeof(ort)atIndex:1];for(NSNumber*k in @[@9,@12,@2,@3,@11])[e setBytes:roi length:sizeof(roi)atIndex:k.unsignedIntegerValue];
  if(strength==1){bindings[@"params_sha256"]=Sha([NSData dataWithBytes:params length:sizeof(params)]);bindings[@"stats_sha256"]=Sha([NSData dataWithBytes:average length:sizeof(average)]);}
 }
 [e dispatchThreads:MTLSizeMake(W,H,1)threadsPerThreadgroup:MTLSizeMake(16,16,1)];[e endEncoding];[cb commit];[cb waitUntilCompleted];if(cb.error){Put(@{@"error":cb.error.description,@"operator":op},[out stringByAppendingPathComponent:@"native-error.json"]);exit(5);}return Read(output);
 };
 for(NSNumber*s in @[@0,@0.5,@1]){@autoreleasepool{
  float strength=s.floatValue;NSData*y=eval(source,strength);const __fp16*target=y.bytes;NSString*stem=[NSString stringWithFormat:@"%@-%g",op,strength];[y writeToFile:[out stringByAppendingPathComponent:[stem stringByAppendingString:@"-native.f16"]]atomically:YES];
  NSMutableData*xx=[NSMutableData dataWithLength:N*16],*quant=[source mutableCopy];float*x=xx.mutableBytes;__fp16*v=quant.mutableBytes;uint8_t*eligible=calloc(N,1);for(NSUInteger i=0;i<N;i++){eligible[i]=1;for(int c=0;c<4;c++)x[i*4+c]=target[i*4+c];for(int c=0;c<3;c++)if(!isfinite(target[i*4+c])||target[i*4+c]<=1./255)eligible[i]=0;}
  NSMutableArray*steps=[NSMutableArray new];for(int it=0;it<24;it++){@autoreleasepool{
   for(NSUInteger i=0;i<N*4;i++)v[i]=(__fp16)x[i];NSData*z=eval(quant,strength);const __fp16*r=z.bytes;NSUInteger failed=0;float maximum=0;for(NSUInteger i=0;i<N;i++){float rel=0;for(int c=0;c<3;c++){rel=fmaxf(rel,fabsf((float)r[i*4+c]-target[i*4+c])/fmaxf(fabsf(target[i*4+c]),1e-12f));}if(eligible[i]){if(rel>1e-3f)for(int c=0;c<3;c++)x[i*4+c]+=(float)target[i*4+c]-r[i*4+c];failed+=rel>1e-3f;maximum=fmaxf(maximum,rel);}}
   [steps addObject:@{@"iteration":@(it),@"failed":@(failed),@"max_relative":@(maximum)}];if(!failed)break;
  }}
  for(NSUInteger i=0;i<N*4;i++)v[i]=(__fp16)x[i];NSData*rt=eval(quant,strength);[xx writeToFile:[out stringByAppendingPathComponent:[stem stringByAppendingString:@"-inverse.f32"]]atomically:YES];[rt writeToFile:[out stringByAppendingPathComponent:[stem stringByAppendingString:@"-roundtrip.f16"]]atomically:YES];
  [results addObject:@{@"operator":op,@"strength":s,@"steps":steps,@"input_sha256":Sha(source),@"native_sha256":Sha(y),@"inverse_f32_sha256":Sha(xx),@"roundtrip_sha256":Sha(rt),@"original_input_used_as_seed":@NO,@"context_frozen_during_inverse":@YES}];free(eligible);
 }}
 facts[[op stringByAppendingString:@"-bindings"]]=bindings;
 }}
 facts[@"rows"]=results;facts[@"os"]=NSProcessInfo.processInfo.operatingSystemVersionString;facts[@"device"]=d.name;facts[@"library_sha256"]=Sha([NSData dataWithContentsOfFile:libpath]);facts[@"scope"]=@"Native final units only; real primary/skin/person, artificial frozen blur/stats/guided reconstruction. Not original capture Studio undo.";Put(facts,[out stringByAppendingPathComponent:@"native.json"]);return 0;
}}
