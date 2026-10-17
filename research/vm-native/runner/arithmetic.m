#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
int main(int argc,char **argv){@autoreleasepool{
 if(argc!=2)return 2;NSString *out=@(argv[1]);[[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:YES attributes:nil error:NULL];
 id<MTLDevice> d=MTLCreateSystemDefaultDevice();NSError *error=nil;
 NSString *src=@"#include <metal_stdlib>\nusing namespace metal;\nkernel void arithmetic(device const float *p [[buffer(0)]],device half *q [[buffer(1)]],uint i [[thread_position_in_grid]]){half a=half(p[i*3]),b=half(p[i*3+1]),t=half(p[i*3+2]);q[i*8]=mix(a,b,t);q[i*8+1]=a+(b-a)*t;q[i*8+2]=a*(half(1)-t)+b*t;q[i*8+3]=fma(b-a,t,a);q[i*8+4]=dot(half3(a,b,t),half3(.299h,.587h,.114h));q[i*8+5]=pow(a+half(.0001),b*half(2)+half(.5));q[i*8+6]=sqrt(a);q[i*8+7]=atan2(a,b);}\n";
 MTLCompileOptions *o=[MTLCompileOptions new];o.fastMathEnabled=YES;id<MTLLibrary> lib=[d newLibraryWithSource:src options:o error:&error];
 if(!lib){[error.description writeToFile:[out stringByAppendingPathComponent:@"compile-error.txt"] atomically:YES encoding:NSUTF8StringEncoding error:NULL];return 3;}
 id<MTLComputePipelineState> ps=[d newComputePipelineStateWithFunction:[lib newFunctionWithName:@"arithmetic"] error:&error];if(!ps)return 4;
 NSUInteger n=65536;NSMutableData *input=[NSMutableData dataWithLength:n*3*4];float *p=input.mutableBytes;uint32_t seed=20261018;
 for(NSUInteger i=0;i<n*3;i++){seed=1664525u*seed+1013904223u;p[i]=(seed>>8)*(1.f/16777216.f);}
 id<MTLBuffer> ib=[d newBufferWithBytes:input.bytes length:input.length options:MTLResourceStorageModeShared],ob=[d newBufferWithLength:n*8*2 options:MTLResourceStorageModeShared];id<MTLCommandQueue> queue=[d newCommandQueue];id<MTLCommandBuffer> cb=[queue commandBuffer];id<MTLComputeCommandEncoder> enc=[cb computeCommandEncoder];[enc setComputePipelineState:ps];[enc setBuffer:ib offset:0 atIndex:0];[enc setBuffer:ob offset:0 atIndex:1];[enc dispatchThreads:MTLSizeMake(n,1,1) threadsPerThreadgroup:MTLSizeMake(128,1,1)];[enc endEncoding];[cb commit];[cb waitUntilCompleted];if(cb.error)return 5;
 [input writeToFile:[out stringByAppendingPathComponent:@"input.f32"] atomically:YES];[[NSData dataWithBytes:ob.contents length:ob.length]writeToFile:[out stringByAppendingPathComponent:@"output.f16"] atomically:YES];
 NSDictionary *m=@{@"device":d.name,@"shape_input":@[@(n),@3],@"shape_output":@[@(n),@8],@"dtype_input":@"<f4",@"dtype_output":@"<f2",@"fast_math":@YES,@"source":src,@"os":NSProcessInfo.processInfo.operatingSystemVersionString};[[NSJSONSerialization dataWithJSONObject:m options:NSJSONWritingPrettyPrinted error:NULL]writeToFile:[out stringByAppendingPathComponent:@"metadata.json"] atomically:YES];return 0;
}}
