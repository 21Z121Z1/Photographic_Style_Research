#import "../texture-producer-20261020/spi_call.h"

int main(int argc,char **argv) {
    @autoreleasepool {
        if(argc!=2)return 64;
        dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",RTLD_NOW|RTLD_LOCAL);
        NSMutableArray *rows=[NSMutableArray new];BOOL passed=YES;
        for(NSNumber *angle in @[@(-47.5),@(-0.75),@0,@19.25,@89.5]) {
            id person=Make(@"CMITextureStylesPersonInputData");
            Call(person,@"setUnitOfAngle:",@[@0]);
            for(NSString *setter in @[@"setFacePitch:",@"setFaceRoll:",@"setFaceYaw:"])Call(person,setter,@[angle]);
            NSDictionary *raw=Call(person,@"dictionaryRepresentation",@[]),*serialized=PersonDictionary(person);
            id readback=Call(NSClassFromString(@"CMITextureStylesPersonInputData"),@"personDataFromDictionary:",@[serialized]);
            NSMutableDictionary *actual=[NSMutableDictionary new];
            for(NSString *key in @[@"facePitch",@"faceRoll",@"faceYaw"]) {
                NSNumber *getter=Call(readback,key,@[]);actual[key]=getter;
                passed &= fabs(getter.doubleValue-angle.doubleValue)<1e-5;
            }
            [rows addObject:@{@"input_signed_degrees":angle,@"unadjusted_native_dictionary":raw,@"lossless_serialization":serialized,@"native_readback_getters":actual}];
        }
        Write(@{@"passed":@(passed),@"rows":rows,@"scope":@"original native signed float setters/getters and dictionary parser; no Apple code patched"},@(argv[1]));return passed?0:1;
    }
}
