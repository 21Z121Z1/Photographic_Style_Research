#define main S56RetainedUnusedMain
#include "histogram_probe_s56.m"
#undef main

int main(int argc,char **argv){@autoreleasepool{
 if(argc!=3)return 2;NSMutableDictionary*r=[@{@"rows":[NSMutableArray new],@"synthetic_only":@YES,@"full_host_dispatch":@NO}mutableCopy];int rc=0;
 @try{
  Require(dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",RTLD_NOW|RTLD_LOCAL)!=NULL,@"dlopen");
  r[@"CMImaging"]=CMIUUID();Require([r[@"CMImaging"][@"UUID"]caseInsensitiveCompare:@"3CCD434E-B1E0-3F14-8EF6-E29D58379BE8"]==NSOrderedSame,@"UUID");
  Method residency=class_getClassMethod(NSClassFromString(@"CMIMetalResourceCache"),NSSelectorFromString(@"_enableResidencySets"));if(residency)method_setImplementation(residency,(IMP)S55No);
  id<MTLDevice>dev=MTLCreateSystemDefaultDevice();Require(dev!=nil,@"Metal unavailable");r[@"AppleFamily4"]=@([dev supportsFamily:MTLGPUFamilyApple4]);Require([dev supportsFamily:MTLGPUFamilyApple4],@"Family4");id<MTLCommandQueue>queue=[dev newCommandQueue];
  id renderer=[[NSClassFromString(@"CMISmartStyleMetalRendererV1")alloc]initWithOptionalMetalCommandQueue:queue];Require(renderer!=nil,@"renderer");
  id<MTLTexture>dummy=Texture(dev,16,16,NO,[NSMutableData dataWithLength:2048]);id<MTLTexture>gtc=Texture(dev,256,1,YES,[NSMutableData dataWithLength:512]);
  [renderer setValue:dummy forKey:@"inputImageTexture"];[renderer setValue:dummy forKey:@"inputLinearImageTexture"];[renderer setValue:gtc forKey:@"inputGlobalToneCurveTexture"];
  r[@"prepare_status"]=@([renderer prepareToProcess:1]);Require([r[@"prepare_status"]intValue]==0,@"prepare");
  id<MTLComputePipelineState>pso=ObjectIvar(renderer,"_updateBaseGainWithStats");Require(pso!=nil,@"original baseGain PSO");
  r[@"PSO"]=@{@"ivar":@"_updateBaseGainWithStats",@"original_host_object":@YES,@"class":NSStringFromClass([(id)pso class]),@"label":pso.label?:@"",@"custom_synthetic_bindings":@YES,@"source_buffers_at_indices":@[@1,@3]};
  NSDictionary*spec=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@(argv[1])]options:0 error:NULL];Require(spec!=nil,@"cases");
  for(NSDictionary*c in spec[@"cases"]){@autoreleasepool{
   r[@"checkpoint"]=c[@"id"];NSMutableData*params=[NSMutableData dataWithLength:672],*stats=[NSMutableData dataWithLength:10640];memset(params.mutableBytes,0x5a,672);
   ((float*)params.mutableBytes)[6]=123.0f;((float*)params.mutableBytes)[7]=Number(c,@"exposure");*(float*)((uint8_t*)stats.mutableBytes+10636)=Number(c,@"avg_main");*(float*)((uint8_t*)stats.mutableBytes+10624)=Number(c,@"avg_linear");
   id<MTLBuffer>p=[dev newBufferWithBytes:params.bytes length:672 options:MTLResourceStorageModeShared],s=[dev newBufferWithBytes:stats.bytes length:10640 options:MTLResourceStorageModeShared];
   id<MTLCommandBuffer>cb=[queue commandBuffer];id<MTLComputeCommandEncoder>e=[cb computeCommandEncoder];[e setComputePipelineState:pso];[e setBuffer:p offset:0 atIndex:1];[e setBuffer:s offset:0 atIndex:3];[e dispatchThreadgroups:MTLSizeMake(1,1,1)threadsPerThreadgroup:MTLSizeMake(1,1,1)];[e endEncoding];[cb commit];[cb waitUntilCompleted];Require(cb.error==nil,cb.error.description?:@"GPU");
   float out=*((float*)p.contents+6);uint32_t bits;memcpy(&bits,&out,4);NSUInteger outside=0;const uint8_t*a=params.bytes,*b=p.contents;for(NSUInteger k=0;k<672;k++)if((k<24||k>=28)&&a[k]!=b[k])outside++;
   BOOL statsUnchanged=[SHA(stats)isEqual:SHA([NSData dataWithBytes:s.contents length:10640])];Require(outside==0&&statsUnchanged,@"unexpected context mutation");
   NSMutableDictionary*row=[@{@"id":c[@"id"],@"output_bits":@(bits),@"finite":@(isfinite(out)),@"nan":@(isnan(out)),@"infinite":@(isinf(out)),@"outside_gain_changed_bytes":@(outside),@"stats_SHA_unchanged":@(statsUnchanged),@"input_params_sha256":SHA(params),@"input_stats_sha256":SHA(stats)}mutableCopy];if(isfinite(out))row[@"output"]=@(out);[(NSMutableArray*)r[@"rows"]addObject:row];
  }}r[@"completed"]=@YES;r[@"checkpoint"]=@"complete";
 }@catch(NSException*e){r[@"completed"]=@NO;r[@"exception"]=e.description;rc=3;}
 @try{Save(r,@(argv[2]));}@catch(NSException*e){return 4;}return rc;
}}
