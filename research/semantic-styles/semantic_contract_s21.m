#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <CommonCrypto/CommonDigest.h>
#include <math.h>
#include <stdint.h>

static void Save(id o,NSString*p){NSError*e=nil;NSData*d=[NSJSONSerialization dataWithJSONObject:o options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:&e];if(!d)@throw[NSException exceptionWithName:@"JSON" reason:e.description userInfo:nil];if(![d writeToFile:p options:NSDataWritingWithoutOverwriting error:&e])@throw[NSException exceptionWithName:@"Write" reason:e.description userInfo:nil];}
static NSString*Digest(NSData*d){unsigned char z[32];CC_SHA256(d.bytes,(CC_LONG)d.length,z);NSMutableString*s=[NSMutableString new];for(int i=0;i<32;i++)[s appendFormat:@"%02x",z[i]];return s;}
int main(int argc,char**argv){@autoreleasepool{
 if(argc!=2)return 2;NSString*out=@(argv[1]);[[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:YES attributes:nil error:NULL];
 id<MTLDevice>d=MTLCreateSystemDefaultDevice();if(!d){Save(@{@"metal":@NO},[out stringByAppendingPathComponent:@"capabilities.json"]);return 3;}
 NSMutableDictionary*families=[NSMutableDictionary new];
 for(int i=1;i<=10;i++)families[[NSString stringWithFormat:@"Apple%d",i]]=@([d supportsFamily:(MTLGPUFamily)((NSInteger)MTLGPUFamilyApple1+i-1)]);
 families[@"Mac1"]=@([d supportsFamily:MTLGPUFamilyMac1]);families[@"Mac2"]=@([d supportsFamily:MTLGPUFamilyMac2]);
 families[@"Common1"]=@([d supportsFamily:MTLGPUFamilyCommon1]);families[@"Common2"]=@([d supportsFamily:MTLGPUFamilyCommon2]);families[@"Common3"]=@([d supportsFamily:MTLGPUFamilyCommon3]);
 MTLCompileOptions*defaults=[MTLCompileOptions new];
 NSString*path=@"/System/Library/PrivateFrameworks/CMImaging.framework/Resources/default.metallib";NSError*err=nil;id<MTLLibrary>original=[d newLibraryWithFile:path error:&err];
 NSMutableDictionary*cap=[@{@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"device":d.name,@"architecture":d.architecture.name?:@"unknown",@"families":families,@"AppleFamily4_contract_prerequisite_reported":families[@"Apple4"],@"default_fastMathEnabled":@(defaults.fastMathEnabled),@"default_mathMode":@(defaults.mathMode),@"default_mathFloatingPointFunctions":@(defaults.mathFloatingPointFunctions),@"original_metallib_sha256":Digest([NSData dataWithContentsOfFile:path]),@"original_consumer_function_listed":@([original.functionNames containsObject:@"renderFinalAdjustments"]),@"original_psos_recompiled_or_changed":@NO,@"photos_used":@NO,@"purpose":@"Numerical-contract qualification; not an inverse or bit-exact model-fitting test."}mutableCopy];
 Save(cap,[out stringByAppendingPathComponent:@"capabilities.json"]);
 // Own synthetic kernel illustrates allowed reassociation. Its results cannot
 // prove a pointwise error envelope for the original Apple consumer.
 NSString*source=@"#include <metal_stdlib>\nusing namespace metal; kernel void cancellation(const device float*x[[buffer(0)]],device float4*y[[buffer(1)]],uint i[[thread_position_in_grid]]){float a=x[i];float f=(a+16777216.0f)-16777216.0f;half h=half(a);half k=(h+half(2048.0f))-half(2048.0f);y[i]=float4(f,float(k),a,float(h));}\n";
 float inputs[]={.25f,-.25f,.5f,-.5f,.75f,-.75f,1.f,-1.f,1.25f,-1.25f,2.f,-2.f};NSUInteger n=sizeof(inputs)/sizeof(inputs[0]);
 id<MTLBuffer>ib=[d newBufferWithBytes:inputs length:sizeof(inputs) options:MTLResourceStorageModeShared],ob=[d newBufferWithLength:n*16 options:MTLResourceStorageModeShared];id<MTLCommandQueue>q=[d newCommandQueue];NSMutableArray*rows=[NSMutableArray new];
 for(int mode=0;mode<3;mode++){@autoreleasepool{
  MTLCompileOptions*o=[MTLCompileOptions new];o.mathMode=mode==0?MTLMathModeSafe:mode==1?MTLMathModeRelaxed:MTLMathModeFast;o.mathFloatingPointFunctions=MTLMathFloatingPointFunctionsPrecise;
  id<MTLLibrary>lib=[d newLibraryWithSource:source options:o error:&err];id<MTLComputePipelineState>ps=lib?[d newComputePipelineStateWithFunction:[lib newFunctionWithName:@"cancellation"] error:&err]:nil;
  if(!ps){[rows addObject:@{@"mode":@(mode),@"error":err.description?:@"nil pipeline"}];continue;}
  id<MTLCommandBuffer>cb=[q commandBuffer];id<MTLComputeCommandEncoder>e=[cb computeCommandEncoder];[e setComputePipelineState:ps];[e setBuffer:ib offset:0 atIndex:0];[e setBuffer:ob offset:0 atIndex:1];[e dispatchThreads:MTLSizeMake(n,1,1) threadsPerThreadgroup:MTLSizeMake(n,1,1)];[e endEncoding];[cb commit];[cb waitUntilCompleted];if(cb.error){[rows addObject:@{@"mode":@(mode),@"error":cb.error.description}];continue;}
  float*y=ob.contents;NSMutableArray*cases=[NSMutableArray new];NSUInteger fDifferent=0,hDifferent=0;
  for(NSUInteger i=0;i<n;i++){volatile float vf=inputs[i]+16777216.f;float expectedF=vf-16777216.f;volatile __fp16 vh=(__fp16)(inputs[i]+2048.f);__fp16 expectedH=(__fp16)((float)vh-2048.f);fDifferent+=y[4*i]!=expectedF;hDifferent+=y[4*i+1]!=(float)expectedH;[cases addObject:@{@"synthetic_input":@(inputs[i]),@"native_float":@(y[4*i]),@"native_half":@(y[4*i+1]),@"ordered_RN_float_reference":@(expectedF),@"ordered_RN_half_reference":@((float)expectedH)}];}
  [rows addObject:@{@"mathMode":@(o.mathMode),@"mode_name":@[@"safe",@"relaxed",@"fast"][mode],@"mathFloatingPointFunctions":@(o.mathFloatingPointFunctions),@"float_different_from_ordered_RN":@(fDifferent),@"half_different_from_ordered_RN":@(hDifferent),@"cases":cases}];
 }}
 Save(@{@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"device":d.name,@"scope":@"Own synthetic cancellation kernel only. Does not identify actual original consumer lowering or certify its global feasible set.",@"photos_used":@NO,@"rows":rows},[out stringByAppendingPathComponent:@"reassociation.json"]);
 BOOL failed=rows.count!=3;for(NSDictionary*r in rows)failed|=r[@"error"]!=nil;return failed?4:0;
}}
