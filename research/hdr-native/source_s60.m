// Reuse frozen reverse-style and Apple Log source preparation unchanged.
#define main S37SourceMain
#include "source_s37.m"
#undef main
int main(int argc,char **argv){int rc=S37SourceMain(argc,argv);if(rc)return rc;@autoreleasepool{@try{
 NSString*root=@(argv[2]);NSMutableDictionary*facts=[NSMutableDictionary new];
 for(NSString*key in @[@"inputSubjectMatteImage",@"inputSkinMatteImage",@"inputSkyMatteImage"]){NSString*src=[root stringByAppendingPathComponent:[key stringByAppendingString:@".heic"]];if([[NSFileManager defaultManager]fileExistsAtPath:src])facts[key]=Render(RawImage(src),Context(NULL),NULL,[root stringByAppendingPathComponent:[key stringByAppendingString:@".f32"]]);}
 Write37(facts,[root stringByAppendingPathComponent:@"matte-facts.json"]);return 0;
 }@catch(NSException*e){return 6;}}}
