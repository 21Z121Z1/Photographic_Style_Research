// Narrow text-only inventory of Apple's actual producer interfaces.
// No photo inputs, texture creation, image outputs or binary upload.
#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <objc/runtime.h>
#import <dlfcn.h>

static NSArray *methods(Class cls, BOOL meta) {
    unsigned n=0; Method *list=class_copyMethodList(meta?object_getClass(cls):cls,&n);
    NSMutableArray *out=[NSMutableArray array];
    for(unsigned i=0;i<n;i++) {
        Method m=list[i]; const char *sel=sel_getName(method_getName(m));
        Dl_info image={0}; dladdr((void *)method_getImplementation(m),&image);
        [out addObject:@{@"selector":@(sel), @"types":@(method_getTypeEncoding(m)?:""),
            @"role":meta?@"class":@"instance", @"image":image.dli_fname?@(image.dli_fname):@"unknown",
            @"image_relative_IMP":[NSString stringWithFormat:@"0x%llx",(unsigned long long)((uintptr_t)method_getImplementation(m)-(uintptr_t)image.dli_fbase)]}];
    }
    free(list); return out;
}

int main(int argc,const char **argv) {
    @autoreleasepool {
        if(argc!=2)return 2;
        NSFileManager *fm=NSFileManager.defaultManager;
        NSMutableArray *loads=[NSMutableArray array];
        for(NSString *path in @[@"/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",@"/System/Library/PrivateFrameworks/PhotoImaging.framework/PhotoImaging",@"/System/Library/PrivateFrameworks/CMCapture.framework/CMCapture"]){
            void *h=dlopen(path.fileSystemRepresentation,RTLD_NOW|RTLD_LOCAL);
            const char *e=h?NULL:dlerror();
            [loads addObject:@{@"path":path,@"loaded":@(h!=NULL),@"error":e?@(e):@""}];
        }
        NSMutableArray *bundles=[NSMutableArray array];
        for(NSString *path in @[@"/System/Library/VideoProcessors/SmartStyleV1.bundle",@"/System/Library/VideoProcessors/SmartStyleV2.bundle",@"/System/Library/VideoProcessors/SmartStyle.bundle"]){
            BOOL exists=[fm fileExistsAtPath:path]; NSBundle *b=exists?[NSBundle bundleWithPath:path]:nil;
            NSMutableDictionary *record=[@{@"path":path,@"exists":@(exists),@"executable":b.executablePath?:@""} mutableCopy];
            if(b){
                NSError *error=nil;
                @try { record[@"loaded"]=@([b loadAndReturnError:&error]);record[@"error"]=error.localizedDescription?:@""; }
                @catch(NSException *e){record[@"loaded"]=@NO;record[@"exception"]=e.name;record[@"error"]=e.reason?:@"";}
            }
            [bundles addObject:record];
        }
        NSMutableArray *classes=[NSMutableArray array];
        int count=objc_getClassList(NULL,0); Class *list=calloc((size_t)count,sizeof(Class));
        int actual=objc_getClassList(list,count); if(actual>count)actual=count;
        NSArray *queries=@[@"createLinearThumbnailFromMetadata:ltmThumbnailPixelBuffer:cameraInfo:applyGDC:toPixelBuffer:",@"createLinearThumbnailFromMetadata:postLTMThumbnailPixelBuffer:cameraInfo:applyGDC:cropToPreLTMBounds:toPixelBuffer:",@"createLinearThumbnailFromMetadata:preLTMThumbnailPixelBuffer:postLTMThumbnailPixelBuffer:cameraInfo:applyGDC:cropToPreLTMBounds:toPixelBuffer:"];
        for(int i=0;i<actual;i++){
            Class cl=list[i];NSString *name=NSStringFromClass(cl);BOOL selected=[name containsString:@"SmartStyle"];
            for(NSString *q in queries)if(class_getInstanceMethod(cl,NSSelectorFromString(q)))selected=YES;
            if(!selected)continue;
            NSMutableArray *found=[NSMutableArray array];
            for(NSString *q in queries)if(class_getInstanceMethod(cl,NSSelectorFromString(q)))[found addObject:q];
            const char *image=class_getImageName(cl);
            [classes addObject:@{@"class":name,@"class_image":image?@(image):@"unknown",@"producer_selectors_present":found,@"methods":[methods(cl,NO) arrayByAddingObjectsFromArray:methods(cl,YES)]}];
        }
        free(list);
        id<MTLDevice> device=MTLCreateSystemDefaultDevice();
        NSError *enumerationError=nil;NSArray *directory=[fm contentsOfDirectoryAtPath:@"/System/Library/VideoProcessors" error:&enumerationError];
        NSDictionary *result=@{@"stage":@"S108 actual-producer interface availability",@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"Metal_available":@(device!=nil),@"Metal_device":device.name?:@"",@"loads":loads,@"bundles":bundles,@"VideoProcessors_children":directory?:@[],@"directory_error":enumerationError.localizedDescription?:@"",@"classes":classes,@"native_image_computation":@NO,@"photo_inputs":@0,@"Apple_binary_uploaded":@NO,@"scope":@"Availability/metadata only. No proof of camera equivalence, curve application or pixel accuracy."};
        NSData *data=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL];
        if(![data writeToFile:@(argv[1]) options:NSDataWritingAtomic error:NULL])return 3;
        puts("producer interface inventory complete (text only)");
    }
    return 0;
}
