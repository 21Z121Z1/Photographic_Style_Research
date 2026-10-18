#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <CommonCrypto/CommonDigest.h>
#include <zlib.h>
static NSString*SHA(NSData*d){unsigned char b[CC_SHA256_DIGEST_LENGTH];CC_SHA256(d.bytes,(CC_LONG)d.length,b);NSMutableString*s=[NSMutableString new];for(int i=0;i<CC_SHA256_DIGEST_LENGTH;i++)[s appendFormat:@"%02x",b[i]];return s;}
int main(int argc,char**argv){@autoreleasepool{
 if(argc<2)return 2;NSString*out=@(argv[1]);[[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:YES attributes:nil error:NULL];
 NSString*source=@"#include <metal_stdlib>\nusing namespace metal;kernel void scalar_atan(device const half2*p[[buffer(0)]],device half*q[[buffer(1)]],uint i[[thread_position_in_grid]]){q[i]=atan2(p[i].x,p[i].y);}\n";
 id<MTLDevice>d=MTLCreateSystemDefaultDevice();NSError*error=nil;MTLCompileOptions*o=[MTLCompileOptions new];o.fastMathEnabled=YES;id<MTLLibrary>l=[d newLibraryWithSource:source options:o error:&error];id<MTLComputePipelineState>ps=l?[d newComputePipelineStateWithFunction:[l newFunctionWithName:@"scalar_atan"]error:&error]:nil;if(!ps){[error.description writeToFile:[out stringByAppendingPathComponent:@"error.txt"]atomically:YES encoding:NSUTF8StringEncoding error:NULL];return 3;}
 NSUInteger side=1024,n=side*side,total=n*4;id<MTLBuffer>ib=[d newBufferWithLength:total*4 options:MTLResourceStorageModeShared],ob=[d newBufferWithLength:total*2 options:MTLResourceStorageModeShared];id<MTLCommandQueue>q=[d newCommandQueue];NSMutableArray*rows=[NSMutableArray new];NSFileHandle*old=argc>=3?[NSFileHandle fileHandleForReadingAtPath:@(argv[2])]:nil;uint64_t differences[4]={0,0,0,0};
 for(int delta=-29;delta<=29;delta++){@autoreleasepool{
  int eb=-(int)floor(delta/2.0),ea=delta+eb;uint16_t*p=ib.contents;
  // Signed bits arrive from memory. The shader contains one scalar atan2 call,
  // with no explicit argument negations and no common subexpressions across quadrants.
  for(NSUInteger i=0;i<n;i++)for(int quadrant=0;quadrant<4;quadrant++){p[(i*4+quadrant)*2]=(uint16_t)(((ea+15)<<10)|(i>>10)|((quadrant&1)?0x8000:0));p[(i*4+quadrant)*2+1]=(uint16_t)(((eb+15)<<10)|(i&1023)|((quadrant&2)?0x8000:0));}
  id<MTLCommandBuffer>cb=[q commandBuffer];id<MTLComputeCommandEncoder>e=[cb computeCommandEncoder];[e setComputePipelineState:ps];[e setBuffer:ib offset:0 atIndex:0];[e setBuffer:ob offset:0 atIndex:1];[e dispatchThreads:MTLSizeMake(total,1,1)threadsPerThreadgroup:MTLSizeMake(128,1,1)];[e endEncoding];[cb commit];[cb waitUntilCompleted];if(cb.error)return 4;
  const uint16_t*v=ob.contents;NSData*oldData=nil;if(old){[old seekToFileOffset:(uint64_t)(delta+29)*n*8];oldData=[old readDataOfLength:n*8];if(oldData.length!=n*8)return 5;const uint16_t*ov=oldData.bytes;for(NSUInteger i=0;i<n;i++)for(int quadrant=0;quadrant<4;quadrant++)differences[quadrant]+=v[i*4+quadrant]!=ov[i*4+quadrant];}
  for(int quadrant=0;quadrant<4;quadrant++){@autoreleasepool{
   NSMutableData*plane=[NSMutableData dataWithLength:n*2];uint16_t*pv=plane.mutableBytes;int32_t maxAbs=0;
   for(NSUInteger y=0;y<side;y++)for(NSUInteger x=0;x<side;x++){NSUInteger i=y*side+x;pv[i]=v[i*4+quadrant];if(x)maxAbs=MAX(maxAbs,abs((int32_t)pv[i]-pv[i-1]));}
   NSUInteger deltaBytes=maxAbs<=127?1:4;NSMutableData*raw=[NSMutableData dataWithLength:side*2+n*deltaBytes];uint16_t*first=raw.mutableBytes;for(NSUInteger y=0;y<side;y++)first[y]=pv[y*side];
   for(NSUInteger y=0;y<side;y++)for(NSUInteger x=0;x<side;x++){NSUInteger i=y*side+x;int32_t difference=x?(int32_t)pv[i]-pv[i-1]:0;if(deltaBytes==1)((int8_t*)((char*)raw.mutableBytes+side*2))[i]=(int8_t)difference;else((int32_t*)((char*)raw.mutableBytes+side*2))[i]=difference;}
   uLongf capacity=compressBound((uLong)raw.length);NSMutableData*z=[NSMutableData dataWithLength:capacity];if(compress2(z.mutableBytes,&capacity,raw.bytes,(uLong)raw.length,6)!=Z_OK)return 6;z.length=capacity;NSString*name=[NSString stringWithFormat:@"atan-d%+d-q%d.dx.zlib",delta,quadrant];[z writeToFile:[out stringByAppendingPathComponent:name]atomically:YES];
   [rows addObject:@{@"delta_exponent":@(delta),@"quadrant":@(quadrant),@"a_exponent":@(ea),@"b_exponent":@(eb),@"shape":@[@1024,@1024],@"delta_dtype":deltaBytes==1?@"i1":@"<i4",@"file":name,@"compressed_bytes":@(z.length),@"compressed_sha256":SHA(z),@"raw_f16_sha256":SHA(plane),@"max_abs_horizontal_word_delta":@(maxAbs)}];
  }}
 }}
 [old closeFile];NSDictionary*m=@{@"schema":@1,@"source":source,@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"device":d.name,@"input_construction":@"All 1024x1024 normal half mantissas, exponent differences -29..29, all four quadrants. Sign bits are in input memory, never shader negation expressions.",@"quadrants":@[@"+a,+b",@"-a,+b",@"+a,-b",@"-a,-b"],@"encoding":@"zlib(1024 little-endian uint16 first-column words, then 1024x1024 signed horizontal word deltas, column zero delta=0)",@"rows":rows,@"old_negated_shader_differences_by_quadrant":@[@(differences[0]),@(differences[1]),@(differences[2]),@(differences[3])],@"old_comparison_present":@(old!=nil)};[[NSJSONSerialization dataWithJSONObject:m options:NSJSONWritingPrettyPrinted error:NULL]writeToFile:[out stringByAppendingPathComponent:@"manifest.json"]atomically:YES];return 0;
}}
