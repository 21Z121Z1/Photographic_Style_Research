#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <CommonCrypto/CommonDigest.h>
#include <zlib.h>
#include <stdint.h>
static NSString* SHA(NSData*d){unsigned char b[CC_SHA256_DIGEST_LENGTH];CC_SHA256(d.bytes,(CC_LONG)d.length,b);NSMutableString*s=[NSMutableString new];for(int i=0;i<CC_SHA256_DIGEST_LENGTH;i++)[s appendFormat:@"%02x",b[i]];return s;}
// No photograph or output image is read: complete F32 mantissas are enumerated.
int main(int argc,char**argv){@autoreleasepool{
 if(argc!=2)return 2;NSString*out=@(argv[1]);[[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:YES attributes:nil error:NULL];
 id<MTLDevice>device=MTLCreateSystemDefaultDevice();if(!device)return 3;NSError*error=nil;
 uint32_t powers[]={0x3edc28f6u,0x4014d653u};NSUInteger n=1u<<23;
 NSMutableString*code=[NSMutableString stringWithString:@"#include <metal_stdlib>\nusing namespace metal;\n"];
 for(int p=0;p<2;p++)[code appendFormat:@"kernel void p%d(device float*q[[buffer(0)]],constant uint&base[[buffer(1)]],device atomic_uint*different[[buffer(2)]],uint i[[thread_position_in_grid]]){float x=as_type<float>(base+i);const float power=as_type<float>(0x%08xu);float y=fast::pow(x,power);q[i]=y;float z=pow(x,power);if(as_type<uint>(y)!=as_type<uint>(z))atomic_fetch_add_explicit(different,1u,memory_order_relaxed);}\n",p,powers[p]];
 MTLCompileOptions*options=[MTLCompileOptions new];options.fastMathEnabled=YES;
 id<MTLLibrary>library=[device newLibraryWithSource:code options:options error:&error];
 if(!library){[error.description writeToFile:[out stringByAppendingPathComponent:@"compile-error.txt"]atomically:YES encoding:NSUTF8StringEncoding error:NULL];return 4;}
 id<MTLCommandQueue>queue=[device newCommandQueue];id<MTLBuffer>result=[device newBufferWithLength:n*4 options:MTLResourceStorageModeShared],counter=[device newBufferWithLength:4 options:MTLResourceStorageModeShared];NSMutableArray*rows=[NSMutableArray new];
 for(int p=0;p<2;p++){
  id<MTLComputePipelineState>ps=[device newComputePipelineStateWithFunction:[library newFunctionWithName:[NSString stringWithFormat:@"p%d",p]]error:&error];if(!ps)return 5;
  for(int exponent=-24;exponent<=2;exponent++){@autoreleasepool{
   uint32_t base=(uint32_t)(exponent+127)<<23;*(uint32_t*)counter.contents=0;
   id<MTLCommandBuffer>cb=[queue commandBuffer];id<MTLComputeCommandEncoder>enc=[cb computeCommandEncoder];[enc setComputePipelineState:ps];[enc setBuffer:result offset:0 atIndex:0];[enc setBytes:&base length:4 atIndex:1];[enc setBuffer:counter offset:0 atIndex:2];[enc dispatchThreads:MTLSizeMake(n,1,1)threadsPerThreadgroup:MTLSizeMake(128,1,1)];[enc endEncoding];[cb commit];[cb waitUntilCompleted];if(cb.error)return 6;
   const uint32_t*v=result.contents;NSMutableData*delta=[NSMutableData dataWithLength:n];int8_t*d=delta.mutableBytes;d[0]=0;int64_t minDelta=0,maxDelta=0;
   for(NSUInteger i=1;i<n;i++){int64_t difference=(int64_t)v[i]-v[i-1];minDelta=MIN(minDelta,difference);maxDelta=MAX(maxDelta,difference);if(difference<INT8_MIN||difference>INT8_MAX){fprintf(stderr,"delta overflow p%d e%d at %lu\n",p,exponent,(unsigned long)i);return 7;}d[i]=(int8_t)difference;}
   uLongf capacity=compressBound((uLong)delta.length);NSMutableData*z=[NSMutableData dataWithLength:capacity];int rc=compress2(z.mutableBytes,&capacity,delta.bytes,(uLong)delta.length,6);if(rc!=Z_OK)return 8;z.length=capacity;
   NSString*name=[NSString stringWithFormat:@"pow-%08x-e%+d.d1.zlib",powers[p],exponent];[z writeToFile:[out stringByAppendingPathComponent:name]atomically:YES];
   NSData*raw=[NSData dataWithBytesNoCopy:result.contents length:result.length freeWhenDone:NO];
   [rows addObject:@{@"power_bits":@(powers[p]),@"input_unbiased_exponent":@(exponent),@"n":@(n),@"first_output_bits":@(v[0]),@"delta_dtype":@"i1",@"delta_min":@(minDelta),@"delta_max":@(maxDelta),@"file":name,@"compressed_bytes":@(z.length),@"compressed_sha256":SHA(z),@"raw_f32_sha256":SHA(raw),@"normal_pow_differing_components":@(*(uint32_t*)counter.contents)}];
  }}
 }
 // Positive zero is outside the normal-mantissa tables. Probe it explicitly.
 NSMutableString*special=[NSMutableString stringWithString:@"#include <metal_stdlib>\nusing namespace metal;kernel void special(device const uint*p[[buffer(0)]],device uint2*q[[buffer(1)]],uint i[[thread_position_in_grid]]){float x=as_type<float>(p[i]);q[i]=uint2(as_type<uint>(fast::pow(x,as_type<float>(0x3edc28f6u))),as_type<uint>(fast::pow(x,as_type<float>(0x4014d653u))));}\n"];
 id<MTLLibrary>sl=[device newLibraryWithSource:special options:options error:&error];id<MTLComputePipelineState>sp=sl?[device newComputePipelineStateWithFunction:[sl newFunctionWithName:@"special"]error:&error]:nil;if(!sp)return 9;
 uint32_t patterns[]={0,0x80000000u,1,0x007fffffu,0x3f800000u,0x7f800000u,0x7fc00000u,0xbf800000u};NSUInteger specials=sizeof(patterns)/sizeof(patterns[0]);id<MTLBuffer>ib=[device newBufferWithBytes:patterns length:sizeof(patterns)options:MTLResourceStorageModeShared],ob=[device newBufferWithLength:specials*8 options:MTLResourceStorageModeShared];
 id<MTLCommandBuffer>cb=[queue commandBuffer];id<MTLComputeCommandEncoder>e=[cb computeCommandEncoder];[e setComputePipelineState:sp];[e setBuffer:ib offset:0 atIndex:0];[e setBuffer:ob offset:0 atIndex:1];[e dispatchThreads:MTLSizeMake(specials,1,1)threadsPerThreadgroup:MTLSizeMake(8,1,1)];[e endEncoding];[cb commit];[cb waitUntilCompleted];if(cb.error)return 10;
 NSMutableArray*sr=[NSMutableArray new];const uint32_t*sv=ob.contents;for(NSUInteger i=0;i<specials;i++)[sr addObject:@{@"input_bits":@(patterns[i]),@"output_bits":@[@(sv[i*2]),@(sv[i*2+1])]}];
 NSDictionary*m=@{@"schema":@1,@"device":device.name,@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"source":code,@"special_source":special,@"powers":@[@(powers[0]),@(powers[1])],@"normal_input_domain":@"All 2^23 float32 mantissas at each unbiased exponent -24..2; no interpolation or photo-dependent fitting",@"rows":rows,@"specials":sr,@"dtype":@"<f4",@"encoding":@"zlib(int8 consecutive uint32 output-bit differences), delta[0]=0; reconstruct uint32 cumsum + first_output_bits"};
 [[NSJSONSerialization dataWithJSONObject:m options:NSJSONWritingPrettyPrinted error:NULL]writeToFile:[out stringByAppendingPathComponent:@"manifest.json"]atomically:YES];return 0;
}}
