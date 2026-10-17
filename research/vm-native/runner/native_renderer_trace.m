#define main FilterProbeMain
#include "native_filter_probe.m"
#undef main

@interface NSObject (XDRendererTrace)
- (id<MTLCommandQueue>)metalCommandQueue;
- (int)finishProcessing;
@end
static NSString *XDTraceDirectory;
static NSMutableDictionary *XDKeptTextures;
static NSUInteger XDTraceCounter;
static int (*XDOriginalProcess)(id,SEL);
static int (*XDOriginalRelease)(id,SEL);
static int (*XDOriginalGuided)(id,SEL,id,id,id,id,NSUInteger,float);
static NSMutableArray *XDGuidedCalls;

static int XDGuided(id self,SEL sel,id command,id input,id guide,id output,NSUInteger radius,float epsilon) {
    int status=XDOriginalGuided(self,sel,command,input,guide,output,radius,epsilon);
    if(XDGuidedCalls) [XDGuidedCalls addObject:@{@"object":self,@"input":input,@"guide":guide,@"output":output,
        @"radius":@(radius),@"epsilon":@(epsilon),@"status":@(status)}];
    return status;
}

static NSDictionary *XDTextures(id renderer) {
    NSMutableDictionary *textures=[NSMutableDictionary new];unsigned int n=0;
    Ivar *vars=class_copyIvarList([renderer class],&n);
    for(unsigned int i=0;i<n;i++) {
        const char *type=ivar_getTypeEncoding(vars[i]);NSString *name=@(ivar_getName(vars[i]));
        if(type[0]=='@' && [name containsString:@"Texture"] && ![name containsString:@"Mapped"] && ![name containsString:@"Scale"]) {
            id value=object_getIvar(renderer,vars[i]);
            if([value respondsToSelector:@selector(pixelFormat)] && [value respondsToSelector:@selector(width)])textures[name]=value;
        }
        if(type[0]=='@' && [name hasSuffix:@"Buf"]) {
            id value=object_getIvar(renderer,vars[i]);if([value respondsToSelector:@selector(length)])textures[name]=value;
        }
    }
    free(vars);return textures;
}
static int XDRelease(id self,SEL sel) {
    @synchronized(XDKeptTextures) {
        NSString *key=[NSString stringWithFormat:@"%p",self];
        NSMutableDictionary *saved=[XDKeptTextures[key] mutableCopy] ?: [NSMutableDictionary new];
        [saved addEntriesFromDictionary:XDTextures(self)];XDKeptTextures[key]=saved;
    }
    return XDOriginalRelease(self,sel);
}
static NSDictionary *XDTextureLayout(MTLPixelFormat format) {
    switch(format) {
    case MTLPixelFormatR16Float:return @{@"channels":@1,@"bytes_per_pixel":@2,@"dtype":@"<f2"};
    case MTLPixelFormatR32Float:return @{@"channels":@1,@"bytes_per_pixel":@4,@"dtype":@"<f4"};
    case MTLPixelFormatRG16Float:return @{@"channels":@2,@"bytes_per_pixel":@4,@"dtype":@"<f2"};
    case MTLPixelFormatRG32Float:return @{@"channels":@2,@"bytes_per_pixel":@8,@"dtype":@"<f4"};
    case MTLPixelFormatRGBA16Float:return @{@"channels":@4,@"bytes_per_pixel":@8,@"dtype":@"<f2"};
    case MTLPixelFormatRGBA32Float:return @{@"channels":@4,@"bytes_per_pixel":@16,@"dtype":@"<f4"};
    case MTLPixelFormatR8Unorm:return @{@"channels":@1,@"bytes_per_pixel":@1,@"dtype":@"u1",@"unorm_denominator":@255};
    case MTLPixelFormatR16Unorm:return @{@"channels":@1,@"bytes_per_pixel":@2,@"dtype":@"<u2",@"unorm_denominator":@65535};
    case MTLPixelFormatRG8Unorm:return @{@"channels":@2,@"bytes_per_pixel":@2,@"dtype":@"u1",@"unorm_denominator":@255};
    case MTLPixelFormatRGBA8Unorm:case MTLPixelFormatRGBA8Unorm_sRGB:case MTLPixelFormatBGRA8Unorm:case MTLPixelFormatBGRA8Unorm_sRGB:
        return @{@"channels":@4,@"bytes_per_pixel":@4,@"dtype":@"u1",@"unorm_denominator":@255};
    default:return @{};
    }
}
static void XDDump(id renderer,NSDictionary *textures,NSString *dir,NSMutableDictionary *facts) {
    id<MTLCommandQueue> queue=[renderer metalCommandQueue];id<MTLDevice> device=queue.device;
    NSMutableDictionary *outputs=[NSMutableDictionary new];
    for(NSString *name in textures) {
        id<MTLTexture> t=textures[name];if(![t respondsToSelector:@selector(pixelFormat)])continue;
        NSDictionary *layout=XDTextureLayout(t.pixelFormat);
        NSMutableDictionary *meta=[@{@"width":@(t.width),@"height":@(t.height),@"array_length":@(t.arrayLength),@"pixel_format":@(t.pixelFormat),@"storage_mode":@(t.storageMode),@"label":t.label?:@""} mutableCopy];
        [meta addEntriesFromDictionary:layout];outputs[name]=meta;
        meta[@"shape"]=@[@(t.height),@(t.width),layout[@"channels"]?:@0];
        if(!layout.count || t.width*t.height>4000000 || t.arrayLength!=1 || t.textureType!=MTLTextureType2D)continue;
        NSUInteger tight=t.width*[layout[@"bytes_per_pixel"] unsignedIntegerValue];NSUInteger stride=(tight+255)&~255;
        id<MTLBuffer> buffer=[device newBufferWithLength:stride*t.height options:MTLResourceStorageModeShared];
        id<MTLCommandBuffer> command=[queue commandBuffer];id<MTLBlitCommandEncoder> blit=[command blitCommandEncoder];
        [blit copyFromTexture:t sourceSlice:0 sourceLevel:0 sourceOrigin:MTLOriginMake(0,0,0) sourceSize:MTLSizeMake(t.width,t.height,1)
            toBuffer:buffer destinationOffset:0 destinationBytesPerRow:stride destinationBytesPerImage:stride*t.height];
        [blit endEncoding];[command commit];[command waitUntilCompleted];
        if(command.error){meta[@"error"]=command.error.description;continue;}
        NSMutableData *data=[NSMutableData dataWithLength:tight*t.height];
        for(NSUInteger y=0;y<t.height;y++)memcpy((char *)data.mutableBytes+y*tight,(char *)buffer.contents+y*stride,tight);
        NSString *file=[name stringByAppendingString:@".bin"];[data writeToFile:[dir stringByAppendingPathComponent:file] atomically:YES];meta[@"file"]=file;
    }
    facts[@"textures"]=outputs;
    for(NSString *name in @[@"_paramsBuf",@"_statsBuf",@"_linearStatsBuf"]) {
        Ivar var=class_getInstanceVariable([renderer class],name.UTF8String);id<MTLBuffer> b=(var?object_getIvar(renderer,var):nil) ?: textures[name];
        if(b && b.length<1000000) {
            id<MTLBuffer> readable=b;
            if(b.storageMode==MTLStorageModePrivate) {
                readable=[device newBufferWithLength:b.length options:MTLResourceStorageModeShared];
                id<MTLCommandBuffer> command=[queue commandBuffer];id<MTLBlitCommandEncoder> blit=[command blitCommandEncoder];
                [blit copyFromBuffer:b sourceOffset:0 toBuffer:readable destinationOffset:0 size:b.length];
                [blit endEncoding];[command commit];[command waitUntilCompleted];
                if(command.error){facts[name]=command.error.description;continue;}
            }
            [[NSData dataWithBytes:readable.contents length:readable.length]writeToFile:[dir stringByAppendingPathComponent:[name stringByAppendingString:@".bin"]] atomically:YES];
            facts[name]=@(b.length);
        }
    }
    for(NSString *name in @[@"inputLinearBaseGain",@"baselineExposure",@"inputLinearEncodingGain",@"faceBasedGlobalExposureBoostRatio",@"tuningParameterVariant",@"sceneType",@"logicalImageSize",@"useLiveMetalAllocations"]) {
        @try {facts[name]=Describe([renderer valueForKey:name] ?: NSNull.null);}@catch(NSException *e){facts[name]=e.description;}
    }
}
static int XDProcess(id self,SEL sel) {
    NSString *key=[NSString stringWithFormat:@"%p",self];NSUInteger serial;
    @synchronized(XDKeptTextures) {XDKeptTextures[key]=XDTextures(self);serial=XDTraceCounter++;}
    XDGuidedCalls=[NSMutableArray new];
    int status=XDOriginalProcess(self,sel);
    NSMutableDictionary *facts=[@{@"process_status":@(status),@"serial":@(serial)} mutableCopy];
    @try {
        facts[@"finish_status"]=@([self finishProcessing]);
        NSMutableDictionary *saved;
        @synchronized(XDKeptTextures) {saved=[XDKeptTextures[key] mutableCopy];[XDKeptTextures removeObjectForKey:key];}
        [saved addEntriesFromDictionary:XDTextures(self)];
        NSMutableArray *guidedFacts=[NSMutableArray new];
        for(NSUInteger i=0;i<XDGuidedCalls.count;i++) {
            NSDictionary *call=XDGuidedCalls[i];id<MTLTexture> input=call[@"input"],guide=call[@"guide"],output=call[@"output"];
            NSMutableDictionary *d=[@{@"radius":call[@"radius"],@"epsilon":call[@"epsilon"],@"status":call[@"status"],
                @"input_size":@[@(input.width),@(input.height)],@"guide_size":@[@(guide.width),@(guide.height)],@"output_size":@[@(output.width),@(output.height)]} mutableCopy];
            if([NSProcessInfo.processInfo.environment[@"XD_TONE_GUIDED_REPLAY"] boolValue]) {
                id<MTLCommandQueue> queue=[self metalCommandQueue];
                MTLTextureDescriptor *desc=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:output.pixelFormat width:output.width height:output.height mipmapped:NO];
                desc.storageMode=MTLStorageModePrivate;desc.usage=MTLTextureUsageShaderRead|MTLTextureUsageShaderWrite;
                id<MTLTexture> copy=[queue.device newTextureWithDescriptor:desc];id<MTLCommandBuffer> command=[queue commandBuffer];
                int replay=XDOriginalGuided(call[@"object"],NSSelectorFromString(@"encodeToCommandBuffer:inputTexture:guideTexture:outputTexture:kernelRadius:epsilon:"),command,input,guide,copy,[call[@"radius"] unsignedIntegerValue],[call[@"epsilon"] floatValue]);
                [command commit];[command waitUntilCompleted];d[@"replay_status"]=@(replay);
                if(command.error)d[@"replay_error"]=command.error.description;
                saved[[NSString stringWithFormat:@"guided-%lu-expectedTexture",(unsigned long)i]]=output;
                saved[[NSString stringWithFormat:@"guided-%lu-replayedTexture",(unsigned long)i]]=copy;
                saved[[NSString stringWithFormat:@"guided-%lu-inputTexture",(unsigned long)i]]=input;
                saved[[NSString stringWithFormat:@"guided-%lu-guideTexture",(unsigned long)i]]=guide;
            }
            [guidedFacts addObject:d];
        }
        facts[@"guided_filter_calls"]=guidedFacts;
        XDGuidedCalls=nil;
        NSString *dir=[XDTraceDirectory stringByAppendingPathComponent:[NSString stringWithFormat:@"renderer-%lu",(unsigned long)serial]];
        [[NSFileManager defaultManager]createDirectoryAtPath:dir withIntermediateDirectories:YES attributes:nil error:NULL];
        XDDump(self,saved,dir,facts);
        [[NSJSONSerialization dataWithJSONObject:facts options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL]writeToFile:[dir stringByAppendingPathComponent:@"trace.json"] atomically:YES];
    } @catch(NSException *e){fprintf(stderr,"Trace exception: %s\n",e.description.UTF8String);}
    return status;
}
int main(int argc,char **argv) { @autoreleasepool {
    if(argc!=4)return 2;
    XDTraceDirectory=@(argv[3]);XDKeptTextures=[NSMutableDictionary new];
    dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",RTLD_NOW|RTLD_LOCAL);
    Class cls=NSClassFromString(@"CMISmartStyleMetalRendererV1");Method m=class_getInstanceMethod(cls,NSSelectorFromString(@"process"));
    XDOriginalProcess=(void *)method_getImplementation(m);method_setImplementation(m,(IMP)XDProcess);
    m=class_getInstanceMethod(cls,NSSelectorFromString(@"_releaseIntermediateResources"));
    XDOriginalRelease=(void *)method_getImplementation(m);method_setImplementation(m,(IMP)XDRelease);
    m=class_getInstanceMethod(NSClassFromString(@"CMIGuidedFilter"),NSSelectorFromString(@"encodeToCommandBuffer:inputTexture:guideTexture:outputTexture:kernelRadius:epsilon:"));
    if(strcmp(method_getTypeEncoding(m),"i60@0:8@16@24@32@40Q48f56"))return 7;
    XDOriginalGuided=(void *)method_getImplementation(m);method_setImplementation(m,(IMP)XDGuided);
    return FilterProbeMain(argc,argv);
} }
