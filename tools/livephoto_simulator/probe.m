#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <Metal/Metal.h>
#import <objc/runtime.h>
#import <dlfcn.h>
#import <TargetConditionals.h>

static void emit(NSDictionary *event) {
    NSData *data = [NSJSONSerialization dataWithJSONObject:event options:NSJSONWritingSortedKeys error:nil];
    if (data) { fwrite(data.bytes, 1, data.length, stdout); fputc('\n', stdout); fflush(stdout); }
}
static NSString *str(const char *s) { return s ? @(s) : @""; }
static NSArray *methods(Class c) {
    unsigned n = 0; Method *m = class_copyMethodList(c, &n); NSMutableArray *r = [NSMutableArray array];
    for (unsigned i=0;i<n;i++) [r addObject:@{@"selector":str(sel_getName(method_getName(m[i]))), @"encoding":str(method_getTypeEncoding(m[i]))}];
    free(m); return r;
}
static void dumpClass(NSString *name) {
    Class c = NSClassFromString(name);
    if (!c) { emit(@{@"kind":@"class", @"name":name, @"present":@NO}); return; }
    NSMutableArray *ivars = [NSMutableArray array]; unsigned n=0; Ivar *v=class_copyIvarList(c,&n);
    for(unsigned i=0;i<n;i++) [ivars addObject:@{@"name":str(ivar_getName(v[i])), @"encoding":str(ivar_getTypeEncoding(v[i])), @"offset":@(ivar_getOffset(v[i]))}];
    free(v); NSMutableArray *props=[NSMutableArray array]; objc_property_t *p=class_copyPropertyList(c,&n);
    for(unsigned i=0;i<n;i++) [props addObject:@{@"name":str(property_getName(p[i])), @"attributes":str(property_getAttributes(p[i]))}];
    free(p);
    emit(@{@"kind":@"class", @"name":name, @"present":@YES, @"image":str(class_getImageName(c)), @"superclass":str(class_getName(class_getSuperclass(c))), @"instance_methods":methods(c), @"class_methods":methods(object_getClass(c)), @"ivars":ivars, @"properties":props});
}
int main(int argc, char **argv) { @autoreleasepool {
    emit(@{@"kind":@"environment", @"os":NSProcessInfo.processInfo.operatingSystemVersionString, @"simulator":@(TARGET_OS_SIMULATOR), @"pid":@(getpid())});
    id<MTLDevice> metal=MTLCreateSystemDefaultDevice();
    emit(@{@"kind":@"metal", @"available":@(metal!=nil), @"name":metal.name ?: @""});
    NSArray *frameworks=@[@"Photos", @"PhotoLibraryServices", @"MediaAnalysis", @"MediaAnalysisServices", @"PhotoImaging", @"PhotosUICore", @"PhotosUIPrivate", @"PosterKit", @"PosterBoardServices", @"WallpaperKit"];
    for(NSString *name in frameworks) {
        NSMutableArray *attempts=[NSMutableArray array]; BOOL loaded=NO;
        for(NSString *area in @[@"PrivateFrameworks", @"Frameworks"]) {
            NSString *path=[NSString stringWithFormat:@"/System/Library/%@/%@.framework/%@", area, name, name];
            dlerror(); void *h=dlopen(path.UTF8String,RTLD_LAZY|RTLD_GLOBAL); const char *error=dlerror();
            [attempts addObject:@{@"path":path,@"loaded":@(h!=NULL),@"error":str(error)}];
            if(h) { loaded=YES; break; }
        }
        emit(@{@"kind":@"framework",@"name":name,@"loaded":@(loaded),@"attempts":attempts});
    }
    NSMutableOrderedSet *names=[NSMutableOrderedSet orderedSetWithArray:@[@"PHLivePhoto", @"PIPosterSettlingEffectLoader", @"PIParallaxSegmentationItem", @"PUParallaxLayerStackViewModel", @"VCPSettlingEffectAnalyzer", @"VCPVideoMetaLivePhotoMetaAnalyzer", @"MADService", @"MADServicePrivate"]];
    unsigned count=0; Class *classes=objc_copyClassList(&count);
    for(unsigned i=0;i<count;i++) {
        NSString *n=str(class_getName(classes[i]));
        if([n rangeOfString:@"Settling" options:NSCaseInsensitiveSearch].location!=NSNotFound || [n rangeOfString:@"LivePhotoMeta" options:NSCaseInsensitiveSearch].location!=NSNotFound || [n rangeOfString:@"FRCFrameDrop"].location!=NSNotFound || [n rangeOfString:@"ParallaxSegmentation"].location!=NSNotFound) [names addObject:n];
    } free(classes);
    for(NSString *n in names) dumpClass(n);
    emit(@{@"kind":@"conclusion", @"media_test_run":@NO, @"wallpaper_eligibility":@"not_tested", @"note":@"Runtime presence and selectors only. No success or absence is a device wallpaper eligibility verdict."});
} return 0; }
