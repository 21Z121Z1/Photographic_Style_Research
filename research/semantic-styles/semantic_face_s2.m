// Independent parameter intervention. The frozen consumer sources are included unchanged.
#define main FrozenFilterMain
#include "native_filter_probe.m"
#undef main
static id (*OriginalJ)(id,SEL);
static id ControlledJ(id self,SEL cmd){
 NSString *v=NSProcessInfo.processInfo.environment[@"SEMANTIC_J"];
 return v?@([v doubleValue]):OriginalJ(self,cmd);
}
static BOOL NoResidency(id self,SEL cmd){return NO;}
int main(int argc,char **argv){@autoreleasepool{
 dlopen("/System/Library/PrivateFrameworks/NeutrinoCore.framework/NeutrinoCore",RTLD_NOW|RTLD_LOCAL);
 dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",RTLD_NOW|RTLD_LOCAL);
 Method m=class_getInstanceMethod(NSClassFromString(@"_NUSemanticStyleProperties"),NSSelectorFromString(@"faceBasedGlobalExposureBoostRatio"));
 if(!m||method_getTypeEncoding(m)[0]!='@')return 9;
 OriginalJ=(void*)method_getImplementation(m);method_setImplementation(m,(IMP)ControlledJ);
 m=class_getClassMethod(NSClassFromString(@"CMIMetalResourceCache"),NSSelectorFromString(@"_enableResidencySets"));
 if(m)method_setImplementation(m,(IMP)NoResidency);
 return FrozenFilterMain(argc,argv);
}}
