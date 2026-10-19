#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <objc/runtime.h>
#import <dlfcn.h>
#import <mach-o/dyld.h>
#import <mach-o/loader.h>
#import <CommonCrypto/CommonDigest.h>
#include <math.h>

@interface NSObject(S55Renderer)
- (instancetype)initWithOptionalMetalCommandQueue:(id)queue;
- (int)prepareToProcess:(int)type;
@end

static BOOL S55No(id obj,SEL cmd){return NO;}
static void Require(BOOL ok,NSString *why){if(!ok)@throw [NSException exceptionWithName:@"S55" reason:why userInfo:nil];}
static NSString *SHA(NSData *data){unsigned char h[CC_SHA256_DIGEST_LENGTH];CC_SHA256(data.bytes,(CC_LONG)data.length,h);NSMutableString*s=[NSMutableString new];for(int i=0;i<32;i++)[s appendFormat:@"%02x",h[i]];return s;}
static Ivar FindIvar(id object,const char *name){for(Class c=[object class];c;c=class_getSuperclass(c)){Ivar v=class_getInstanceVariable(c,name);if(v)return v;}return NULL;}
static id ObjectIvar(id object,const char *name){Ivar v=FindIvar(object,name);Require(v&&ivar_getTypeEncoding(v)[0]=='@',@(name));return object_getIvar(object,v);}
static NSDictionary *CMIUUID(void){for(uint32_t i=0;i<_dyld_image_count();i++){const char *path=_dyld_get_image_name(i);if(!strstr(path,"/CMImaging.framework/"))continue;const struct mach_header_64 *h=(void*)_dyld_get_image_header(i);const uint8_t*p=(const uint8_t*)(h+1);for(uint32_t j=0;j<h->ncmds;j++){const struct load_command*c=(void*)p;if(c->cmd==LC_UUID){const struct uuid_command*u=(void*)p;NSUUID*id=[[NSUUID alloc]initWithUUIDBytes:u->uuid];return @{@"UUID":id.UUIDString,@"loaded_path":@(path)};}p+=c->cmdsize;}}return @{};}
static uint16_t H(float x){__fp16 h=(__fp16)x;uint16_t b;memcpy(&b,&h,2);return b;}
static float F(uint16_t b){__fp16 h;memcpy(&h,&b,2);return(float)h;}
static float Number(NSDictionary*c,NSString*k){return[c[k]floatValue];}
static id<MTLTexture> Texture(id<MTLDevice>d,NSUInteger w,NSUInteger h,BOOL single,NSData*data){MTLTextureDescriptor*t=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:single?MTLPixelFormatR16Float:MTLPixelFormatRGBA16Float width:w height:h mipmapped:NO];t.storageMode=MTLStorageModeShared;t.usage=MTLTextureUsageShaderRead|MTLTextureUsageShaderWrite;id<MTLTexture>x=[d newTextureWithDescriptor:t];Require(x!=nil,@"texture allocation");if(data)[x replaceRegion:MTLRegionMake2D(0,0,w,h) mipmapLevel:0 withBytes:data.bytes bytesPerRow:w*(single?2:8)];return x;}
static NSData *Pixels(NSDictionary*c,BOOL linear){NSMutableData*d=[NSMutableData dataWithLength:16*16*8];uint16_t*p=d.mutableBytes;float left=Number(c,linear?@"linear_left":@"main_left"),right=Number(c,linear?@"linear_right":@"main_right");for(int y=0;y<16;y++)for(int x=0;x<16;x++){uint16_t v=H(x<8?left:right);for(int channel=0;channel<3;channel++)p[(y*16+x)*4+channel]=v;p[(y*16+x)*4+3]=H(1);}return d;}
static NSData *ReadTexture(id<MTLTexture>t){NSUInteger n=t.pixelFormat==MTLPixelFormatR16Float?2:8;NSMutableData*d=[NSMutableData dataWithLength:t.width*t.height*n];[t getBytes:d.mutableBytes bytesPerRow:t.width*n fromRegion:MTLRegionMake2D(0,0,t.width,t.height) mipmapLevel:0];return d;}
static void Save(NSDictionary*j,NSString*file){NSError*e=nil;NSData*d=[NSJSONSerialization dataWithJSONObject:j options:NSJSONWritingPrettyPrinted error:&e];Require(d!=nil,e.description?:@"JSON encoding");Require([d writeToFile:file options:NSDataWritingWithoutOverwriting error:&e],e.description?:@"JSON write");}

int main(int argc,char**argv){@autoreleasepool{if(argc!=3)return 2;NSString*out=@(argv[2]);NSMutableDictionary*report=[@{@"synthetic_only":@YES,@"photos_used":@NO,@"full_host_dispatch":@NO,@"old_inverse_fit":@NO,@"rows":[NSMutableArray new]}mutableCopy];int result=0;
@try{
    report[@"checkpoint"]=@"load-framework";
    Require(dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",RTLD_NOW|RTLD_LOCAL)!=NULL,@"CMImaging dlopen");
    report[@"CMImaging"]=CMIUUID();
    Require(report[@"CMImaging"][@"UUID"]!=nil&&[report[@"CMImaging"][@"UUID"]caseInsensitiveCompare:@"3CCD434E-B1E0-3F14-8EF6-E29D58379BE8"]==NSOrderedSame,@"CMI UUID mismatch");
    Method residency=class_getClassMethod(NSClassFromString(@"CMIMetalResourceCache"),NSSelectorFromString(@"_enableResidencySets"));
    if(residency)method_setImplementation(residency,(IMP)S55No);
    report[@"VM_compatibility_override"]=@"Existing _enableResidencySets=NO; no shader or original PSO mutation";
    id<MTLDevice>dev=MTLCreateSystemDefaultDevice();Require(dev!=nil,@"No Metal");id<MTLCommandQueue>queue=[dev newCommandQueue];Require(queue!=nil,@"No command queue");
    report[@"device"]=dev.name;report[@"AppleFamily4"]=@([dev supportsFamily:MTLGPUFamilyApple4]);Require([dev supportsFamily:MTLGPUFamilyApple4],@"Apple Family4 missing");
    NSDictionary*spec=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@(argv[1])]options:0 error:NULL];Require(spec!=nil,@"input cases");
    NSData*zeroRGBA=[NSMutableData dataWithLength:16*16*8];id<MTLTexture>dummy=Texture(dev,16,16,NO,zeroRGBA);
    NSMutableData*gtcData=[NSMutableData dataWithLength:512];for(int i=0;i<256;i++)((uint16_t*)gtcData.mutableBytes)[i]=H((float)i/255.0f);
    id<MTLTexture>gtc=Texture(dev,256,1,YES,gtcData);
    report[@"checkpoint"]=@"original-host-prepare";
    id renderer=[[NSClassFromString(@"CMISmartStyleMetalRendererV1")alloc]initWithOptionalMetalCommandQueue:queue];Require(renderer!=nil,@"renderer init");
    [renderer setValue:dummy forKey:@"inputImageTexture"];[renderer setValue:dummy forKey:@"inputLinearImageTexture"];[renderer setValue:gtc forKey:@"inputGlobalToneCurveTexture"];
    Ivar flag=FindIvar(renderer,"_useSemanticSRL");Require(flag!=NULL,@"SRL flag unavailable");ptrdiff_t flagOffset=ivar_getOffset(flag);uint8_t beforeFlag=*((uint8_t*)(__bridge void*)renderer+flagOffset);Require(beforeFlag==0,@"SRL-before-stats context differs");
    report[@"SRL_flag"]=@{@"offset":@(flagOffset),@"value":@(beforeFlag),@"written":@NO};
    int status=[renderer prepareToProcess:1];report[@"prepare_status"]=@(status);report[@"prepare_mask"]=@1;Require(status==0,@"prepare failed");Require(*((uint8_t*)(__bridge void*)renderer+flagOffset)==0,@"SRL context changed during prepare");
    id<MTLComputePipelineState>pso=ObjectIvar(renderer,"_localHistogramStatsAll");Require(pso!=nil,@"original histogram PSO missing");
    report[@"PSO"]=@{@"class":NSStringFromClass([(id)pso class]),@"label":pso.label?:@"",@"ivar":@"_localHistogramStatsAll",@"original_host_object":@YES,@"custom_dispatch_and_synthetic_bindings":@YES,@"thread_execution_width":@(pso.threadExecutionWidth),@"max_threads":@(pso.maxTotalThreadsPerThreadgroup)};
    Require(pso.maxTotalThreadsPerThreadgroup>=256,@"insufficient threadgroup size");
    NSMutableData*color=[NSMutableData dataWithLength:320];for(int block=0;block<4;block++)for(int i=0;i<3;i++)((float*)((uint8_t*)color.mutableBytes+block*80+16+i*16))[i]=1;
    NSMutableData*roi=[NSMutableData dataWithLength:176];uint16_t*shorts=roi.mutableBytes;shorts[0]=shorts[1]=shorts[2]=shorts[3]=16;
    for(int index=0;index<9;index++){float*p=(float*)((uint8_t*)roi.mutableBytes+16+index*16);p[0]=p[1]=1.0f/16.0f;}
    id<MTLBuffer>intermediate=[dev newBufferWithLength:10575872 options:MTLResourceStorageModeShared];Require(intermediate!=nil,@"stats allocation");
    for(NSDictionary*c in spec[@"cases"]){@autoreleasepool{
        report[@"checkpoint"]=[@"case:"stringByAppendingString:c[@"id"]];
        NSData*mainData=Pixels(c,NO),*linearData=Pixels(c,YES);id<MTLTexture>main=Texture(dev,16,16,NO,mainData),linear=Texture(dev,16,16,NO,linearData);
        NSMutableData*personData=[NSMutableData dataWithLength:512],*skinData=[NSMutableData dataWithLength:512];
        for(int i=0;i<256;i++){((uint16_t*)personData.mutableBytes)[i]=H(Number(c,@"person"));((uint16_t*)skinData.mutableBytes)[i]=H(Number(c,@"skin"));}
        id<MTLTexture>person=Texture(dev,16,16,YES,personData),skin=Texture(dev,16,16,YES,skinData);
        BOOL square=[c[@"curve"]isEqualToString:@"square"];for(int i=0;i<256;i++){float v=(float)i/255.0f;((uint16_t*)gtcData.mutableBytes)[i]=H(square?v*v:v);}
        [gtc replaceRegion:MTLRegionMake2D(0,0,256,1) mipmapLevel:0 withBytes:gtcData.bytes bytesPerRow:512];
        uint16_t poison=0x7e00;NSData*poisonData=[NSData dataWithBytes:&poison length:2];id<MTLTexture>cmap=Texture(dev,1,1,YES,poisonData),dmap=Texture(dev,1,1,YES,poisonData);
        NSMutableData*params=[NSMutableData dataWithLength:672],*stats=[NSMutableData dataWithLength:10640];
        ((float*)params.mutableBytes)[6]=Number(c,@"base_gain");((float*)params.mutableBytes)[7]=Number(c,@"baseline_exposure");
        *(float*)((uint8_t*)stats.mutableBytes+10620)=Number(c,@"lin_max");*(float*)((uint8_t*)stats.mutableBytes+10632)=Number(c,@"ltm_max");
        id<MTLBuffer>p=[dev newBufferWithBytes:params.bytes length:params.length options:MTLResourceStorageModeShared],s=[dev newBufferWithBytes:stats.bytes length:stats.length options:MTLResourceStorageModeShared];
        memset(intermediate.contents,0,intermediate.length);
        id<MTLCommandBuffer>cb=[queue commandBuffer];id<MTLComputeCommandEncoder>e=[cb computeCommandEncoder];[e setComputePipelineState:pso];
        [e setTexture:main atIndex:0];[e setTexture:linear atIndex:1];[e setTexture:gtc atIndex:2];[e setTexture:person atIndex:10];[e setTexture:skin atIndex:11];[e setTexture:cmap atIndex:17];[e setTexture:dmap atIndex:18];
        [e setBytes:color.bytes length:color.length atIndex:0];[e setBuffer:p offset:0 atIndex:1];[e setBuffer:s offset:0 atIndex:3];[e setBuffer:intermediate offset:0 atIndex:4];[e setBytes:roi.bytes length:roi.length atIndex:5];
        [e dispatchThreadgroups:MTLSizeMake(1,1,1)threadsPerThreadgroup:MTLSizeMake(16,16,1)];[e endEncoding];[cb commit];[cb waitUntilCompleted];Require(cb.error==nil,cb.error.description?:@"GPU error");
        NSData*cr=ReadTexture(cmap),*dr=ReadTexture(dmap);uint16_t ch,dh;memcpy(&ch,cr.bytes,2);memcpy(&dh,dr.bytes,2);
        float*q=(float*)((uint8_t*)intermediate.contents+10485760);
        NSMutableArray*local=[NSMutableArray new];for(int i=0;i<10;i++)[local addObject:@[@(q[i*2048]),@(q[i*2048+1])]];
        uint32_t*counts=(uint32_t*)((uint8_t*)intermediate.contents+10567680);
        NSMutableDictionary*row=[@{@"id":c[@"id"],@"c_bits":@(ch),@"d_bits":@(dh),@"local_p50_p98_by_histogram_index":local,@"person_count":@(counts[0]),@"skin_count":@(counts[1024]),
           @"main_sha256":SHA(mainData),@"linear_sha256":SHA(linearData),@"params_sha256":SHA(params),@"stats_sha256":SHA(stats),@"gtc_sha256":SHA(gtcData)}mutableCopy];
        if(isfinite(F(ch)))row[@"c"]=@(F(ch));if(isfinite(F(dh)))row[@"d"]=@(F(dh));
        BOOL untouched=[SHA(ReadTexture(main))isEqual:SHA(mainData)]&&[SHA(ReadTexture(linear))isEqual:SHA(linearData)]&&[SHA(ReadTexture(gtc))isEqual:SHA(gtcData)]&&[SHA([NSData dataWithBytes:p.contents length:672])isEqual:SHA(params)]&&[SHA([NSData dataWithBytes:s.contents length:10640])isEqual:SHA(stats)];
        row[@"inputs_and_external_context_SHA_unchanged"]=@(untouched);Require(untouched,@"input mutation");[(NSMutableArray*)report[@"rows"]addObject:row];
    }}
    report[@"checkpoint"]=@"complete";report[@"completed"]=@YES;
}@catch(NSException*e){report[@"exception"]=e.description;report[@"completed"]=@NO;result=3;}
@try{Save(report,out);}@catch(NSException*e){fprintf(stderr,"%s\n",e.description.UTF8String);return 4;}return result;}}
