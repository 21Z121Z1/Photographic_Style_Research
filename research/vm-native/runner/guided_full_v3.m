#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <objc/runtime.h>
#import <dlfcn.h>
#import <zlib.h>
@interface NSObject(GuidedFullV3)
- (instancetype)initWithDevice:(id)d allocatorType:(int)t;
- (int)setupWithDescriptor:(id)d;
- (instancetype)initWithOptionalCommandQueue:(id)q allocator:(id)a;
- (int)encodeToCommandBuffer:(id)b inputTexture:(id)p guideTexture:(id)i outputTexture:(id)o kernelRadius:(NSUInteger)r epsilon:(float)e;
@end
static BOOL No(id s,SEL c){return NO;}
static void Require(BOOL p,NSString*m){if(!p)@throw[NSException exceptionWithName:@"GuidedFull"reason:m userInfo:nil];}
static id<MTLTexture> Load(id<MTLDevice>d,NSString*root,NSDictionary*m){
 NSArray*s=m[@"shape"];NSUInteger h=[s[0]unsignedIntegerValue],w=[s[1]unsignedIntegerValue];Require([s[2]intValue]==1,@"Three separate R16 calls are required for RGB");
 NSData*b=[NSData dataWithContentsOfFile:[root stringByAppendingPathComponent:m[@"file"]]];Require(b.length==w*h*2,@"Invalid input dimensions");
 MTLTextureDescriptor*t=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatR16Float width:w height:h mipmapped:NO];t.storageMode=MTLStorageModeShared;t.usage=MTLTextureUsageShaderRead;
 id<MTLTexture>x=[d newTextureWithDescriptor:t];Require(x!=nil,@"Input texture allocation failed");[x replaceRegion:MTLRegionMake2D(0,0,w,h)mipmapLevel:0 withBytes:b.bytes bytesPerRow:w*2];return x;
}
static NSDictionary* Save(id<MTLCommandQueue>q,id<MTLTexture>t,NSString*path){
 NSUInteger stride=(t.width*2+255)&~255;id<MTLBuffer>b=[q.device newBufferWithLength:stride*t.height options:MTLResourceStorageModeShared];Require(b!=nil,@"Readback buffer allocation failed");
 id<MTLCommandBuffer>cb=[q commandBuffer];id<MTLBlitCommandEncoder>e=[cb blitCommandEncoder];[e copyFromTexture:t sourceSlice:0 sourceLevel:0 sourceOrigin:MTLOriginMake(0,0,0) sourceSize:MTLSizeMake(t.width,t.height,1)toBuffer:b destinationOffset:0 destinationBytesPerRow:stride destinationBytesPerImage:stride*t.height];[e endEncoding];[cb commit];[cb waitUntilCompleted];Require(cb.error==nil,cb.error.description?:@"Readback failed");
 FILE*f=fopen(path.fileSystemRepresentation,"wb");Require(f!=NULL,@"Cannot create output");z_stream z={0};Require(deflateInit(&z,6)==Z_OK,@"Cannot initialize zlib");unsigned char output[65536];
 for(NSUInteger y=0;y<t.height;y++){
  z.next_in=(unsigned char*)b.contents+y*stride;z.avail_in=(uInt)t.width*2;
  do{z.next_out=output;z.avail_out=sizeof(output);Require(deflate(&z,Z_NO_FLUSH)==Z_OK,@"Compression failed");fwrite(output,1,sizeof(output)-z.avail_out,f);}while(z.avail_in||!z.avail_out);
 }
 int status;do{z.next_out=output;z.avail_out=sizeof(output);status=deflate(&z,Z_FINISH);fwrite(output,1,sizeof(output)-z.avail_out,f);}while(status==Z_OK);Require(status==Z_STREAM_END,@"Compression finish failed");deflateEnd(&z);fclose(f);
 return @{@"file":path.lastPathComponent,@"shape":@[@(t.height),@(t.width),@1],@"dtype":@"<f2",@"compression":@"zlib",@"uncompressed_bytes":@(t.width*t.height*2)};
}
int main(int argc,char**argv){@autoreleasepool{@try{
 if(argc!=3)return 2;NSString*root=@(argv[1]),*out=@(argv[2]);[[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:YES attributes:nil error:NULL];
 Require(dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",RTLD_NOW|RTLD_LOCAL)!=NULL,@"CMImaging dlopen failed");Method no=class_getClassMethod(NSClassFromString(@"CMIMetalResourceCache"),NSSelectorFromString(@"_enableResidencySets"));if(no)method_setImplementation(no,(IMP)No);
 id<MTLDevice>d=MTLCreateSystemDefaultDevice();Require(d!=nil,@"Metal device unavailable");id<MTLCommandQueue>q=[d newCommandQueue];
 id allocator=[[NSClassFromString(@"FigMetalAllocator")alloc]initWithDevice:d allocatorType:2];Require(allocator!=nil,@"Allocator initializer returned nil");id desc=[NSClassFromString(@"FigMetalAllocatorDescriptor")new];[desc setValue:@(192ull*1024*1024)forKey:@"memSize"];[desc setValue:@YES forKey:@"allowFallback"];[desc setValue:@"styles-full-guided-v3"forKey:@"label"];int setup=[allocator setupWithDescriptor:desc];Require(setup==0,@"Allocator setup failed");
 NSDictionary*spec=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:[root stringByAppendingPathComponent:@"fixture.json"]]options:0 error:NULL];Require(spec!=nil,@"Missing fixture");id<MTLTexture>p=Load(d,root,spec[@"input"]),i=Load(d,root,spec[@"guide"]);NSArray*s=spec[@"output_shape"];
 MTLTextureDescriptor*td=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatR16Float width:[s[1]unsignedIntegerValue]height:[s[0]unsignedIntegerValue]mipmapped:NO];td.storageMode=MTLStorageModePrivate;td.usage=MTLTextureUsageShaderRead|MTLTextureUsageShaderWrite;id<MTLTexture>o=[d newTextureWithDescriptor:td];Require(o!=nil,@"Output texture allocation failed");
 id filter=[[NSClassFromString(@"CMIGuidedFilter")alloc]initWithOptionalCommandQueue:q allocator:allocator];Require(filter!=nil,@"CMIGuidedFilter initializer failed");id<MTLCommandBuffer>cb=[q commandBuffer];int status=[filter encodeToCommandBuffer:cb inputTexture:p guideTexture:i outputTexture:o kernelRadius:1 epsilon:.05f];[cb commit];[cb waitUntilCompleted];Require(status==0&&cb.error==nil,cb.error.description?:[NSString stringWithFormat:@"CMIGuidedFilter status %d",status]);
 NSDictionary*layout=Save(q,o,[out stringByAppendingPathComponent:@"output.f16.zlib"]);NSDictionary*result=@{@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"device":d.name,@"status":@(status),@"allocator_setup":@(setup),@"allocator_type":@2,@"radius":@1,@"epsilon":@(.05f),@"output":layout,@"fixture":spec,@"scope":@"Actual CMIGuidedFilter class API on all declared pixels; three scalar channel calls preserve R16 semantics",@"runtime_override":@"CMIMetalResourceCache._enableResidencySets=NO"};[[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL]writeToFile:[out stringByAppendingPathComponent:@"guided-full.json"]atomically:YES];return 0;
 }@catch(NSException*e){fprintf(stderr,"%s\n",e.description.UTF8String);return 3;}}}
