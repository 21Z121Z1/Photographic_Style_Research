#define main FilterProbeMain
#include "native_filter_probe.m"
#undef main
@interface XDStageInput : NSObject
@property(nonatomic,strong) CIImage *image;
- (CIImage *)outputImage:(NSError **)error;
@end
@implementation XDStageInput
- (CIImage *)outputImage:(NSError **)error {return self.image;}
@end
@interface XDStageEnvironment : NSObject
@property(nonatomic,strong) XDStageInput *input;
@property(nonatomic,strong) NSDictionary *settings;
@end
@implementation XDStageEnvironment
@end
int main(int argc,char **argv) { @autoreleasepool {
    if(argc!=3) return 2;
    NSString *resources=@(argv[1]),*out=@(argv[2]);NSError *error=nil;
    if(![[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:NO attributes:nil error:&error])return 3;
    dlopen("/System/Library/PrivateFrameworks/PhotoImaging.framework/PhotoImaging",RTLD_NOW|RTLD_LOCAL);
    NSData *data=[NSData dataWithContentsOfFile:[resources stringByAppendingPathComponent:@"styles.plist"]];
    NSDictionary *stored=[NSPropertyListSerialization propertyListWithData:data options:0 format:NULL error:&error];
    Class cls=NSClassFromString(@"PISemanticStyleLinearThumbnailNode");SEL selector=NSSelectorFromString(@"_evaluateImage:");
    Method method=class_getInstanceMethod(cls,selector);
    if(!method)return 4;
    NSMethodSignature *signature=[NSMethodSignature signatureWithObjCTypes:method_getTypeEncoding(method)];
    if(signature.numberOfArguments!=3 || strcmp(signature.methodReturnType,"@")) return 5;
    XDStageInput *input=[XDStageInput new];
    input.image=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:[resources stringByAppendingPathComponent:@"linear.heic"]]
        options:@{kCIImageColorSpace:NSNull.null,kCIImageApplyOrientationProperty:@NO}];
    XDStageEnvironment *environment=[XDStageEnvironment new];environment.input=input;
    environment.settings=@{@"linearGain":stored[@"i"][@"Gain"],@"linearRangeMin":stored[@"i"][@"OriginalRangeMin"],@"linearRangeMax":stored[@"i"][@"OriginalRangeMax"]};
    // The inspected implementation calls only input.outputImage: and settings
    // on its node dependencies; no node ivars are accessed. Supply those two
    // dependencies to execute this exact compiled stage in isolation.
    id (*evaluate)(id,SEL,NSError **)=(void *)method_getImplementation(method);
    CIImage *result=evaluate(environment,selector,&error);
    CGColorSpaceRef linear=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
    id<MTLDevice> device=MTLCreateSystemDefaultDevice();
    CIContext *unmanaged=[CIContext contextWithMTLDevice:device options:@{kCIContextWorkingColorSpace:NSNull.null,kCIContextOutputColorSpace:NSNull.null,kCIContextWorkingFormat:@(kCIFormatRGBAf)}];
    CIContext *context=[CIContext contextWithMTLDevice:device options:@{kCIContextWorkingColorSpace:(__bridge id)linear,kCIContextOutputColorSpace:(__bridge id)linear,kCIContextWorkingFormat:@(kCIFormatRGBAf)}];
    NSDictionary *codes=Render(input.image,unmanaged,NULL,[out stringByAppendingPathComponent:@"codes.f32"]);
    NSDictionary *output=Render(result,context,linear,[out stringByAppendingPathComponent:@"native_linear.f32"]);
    NSDictionary *facts=@{@"class":NSStringFromClass(cls),@"selector":NSStringFromSelector(selector),@"abi":@(method_getTypeEncoding(method)),@"settings":environment.settings,
        @"codes":codes,@"output":output,@"scope":@"Exact compiled thumbnail stage with controlled upstream CIImage and settings dependencies; not a complete Photos rendering graph.",@"os":NSProcessInfo.processInfo.operatingSystemVersionString};
    [[NSJSONSerialization dataWithJSONObject:facts options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL]writeToFile:[out stringByAppendingPathComponent:@"facts.json"] atomically:YES];
    CGColorSpaceRelease(linear);printf("Native thumbnail stage finished: %s\n",out.UTF8String);return error?6:0;
} }
