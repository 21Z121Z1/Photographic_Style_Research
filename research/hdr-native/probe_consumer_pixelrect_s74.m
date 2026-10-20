// S74: original signed-integer ROI conversion chain; CPU-only finite fixtures.
#include "consumer_cpu_prefix_s74.inc"
#include <stdint.h>
typedef struct { int64_t x,y,w,h; } PixelRect74;
_Static_assert(sizeof(PixelRect74)==32 && _Alignof(PixelRect74)==8,"four signed longs");
typedef PixelRect74 (*From74)(CGRect,long);
typedef PixelRect74 (*Scale74)(PixelRect74,double,double,long);
typedef CGRect (*To74)(PixelRect74);
typedef CGRect (*Flip74)(CGRect,CGRect);
static NSArray*PA74(PixelRect74 p){return @[@(p.x),@(p.y),@(p.w),@(p.h)];}
static uint64_t DB74(double d){uint64_t u;memcpy(&u,&d,8);return u;}
static NSDictionary*Metadata74(intptr_t*sharedSlide){
    Need(dlopen("/System/Library/PrivateFrameworks/PhotoImaging.framework/PhotoImaging",RTLD_NOW|RTLD_LOCAL)!=NULL,@"PI load");
    Need(dlopen("/System/Library/PrivateFrameworks/NeutrinoCore.framework/NeutrinoCore",RTLD_NOW|RTLD_LOCAL)!=NULL,@"NC load");
    intptr_t ps=0,ns=0;NSDictionary*pi=ImageInfo("/PhotoImaging.framework/",&ps),*nc=ImageInfo("/NeutrinoCore.framework/",&ns);
    Need(pi[@"UUID"] && [pi[@"UUID"]caseInsensitiveCompare:@"5F17E1DB-A15E-38C7-9BEC-E081688B62E5"]==NSOrderedSame,@"PI UUID");
    Need(nc[@"UUID"] && [nc[@"UUID"]caseInsensitiveCompare:@"5E0B3F6B-554E-3373-A411-4A4D1CF0A057"]==NSOrderedSame,@"NC UUID");
    Need(ps==ns,@"shared-cache slide");*sharedSlide=ns;
    NSDictionary*getter=Stub(0x1d0088a70ull,ps);Need([getter[@"selector_decoded"]boolValue],@"original CGRect getter unresolved");
    NSMutableArray*imports=[NSMutableArray new];
    for(NSNumber*a in @[@0x1d01aac20ull,@0x1d01aacb0ull,@0x1d01aace0ull,@0x1d01aad90ull]){
        NSDictionary*b=CBinding(a.unsignedLongLongValue,ps);Need([b[@"indirect_pointer_decoded"]boolValue]&&[b[@"target_symbol"][@"exact_address"]boolValue],@"original PI C import");[imports addObject:b];
    }
    NSMutableArray*cg=[NSMutableArray new];
    for(NSNumber*a in @[@0x1c81766d0ull,@0x1c81766e0ull,@0x1c8176690ull,@0x1c81766a0ull]){
        NSDictionary*b=CBinding(a.unsignedLongLongValue,ns);Need([b[@"indirect_pointer_decoded"]boolValue]&&[b[@"target_symbol"][@"exact_address"]boolValue],@"original NC CGRect C import");[cg addObject:b];
    }
    NSMutableArray*literals=[NSMutableArray new];
    for(NSNumber*a in @[@0x1c5cf52a8ull,@0x1c5cf5450ull]){
        double v;memcpy(&v,Read(a.unsignedLongLongValue+ns,8).bytes,8);Need(isfinite(v),@"finite rounding literal");
        [literals addObject:@{@"unslid":Hex(a.unsignedLongLongValue),@"value":@(v),@"bits":Hex(DB74(v))}];
    }
    uint64_t fpcr=0;__asm__ volatile("mrs %0, fpcr":"=r"(fpcr));
    return @{@"PhotoImaging":pi,@"NeutrinoCore":nc,@"same_shared_cache_slide":@YES,@"original_input_CGRect_getter":getter,@"original_PI_C_imports":imports,@"original_NC_CGRect_imports":cg,@"rounding_literals":literals,@"FPCR":Hex(fpcr),@"PixelRect_size":@(sizeof(PixelRect74)),@"PixelRect_alignment":@(_Alignof(PixelRect74)),@"policy":@0};
}
int main(int argc,char**argv){@autoreleasepool{
    if(argc!=4)return 2;
    NSMutableDictionary*out=[@{@"photos":@0,@"image_dispatches":@0,@"full_domain_proof":@NO,@"acceptance_complete":@NO,@"rows":[NSMutableArray new]}mutableCopy];int rc=0;
    @try{
        out[@"checkpoint"]=@"metadata";intptr_t slide=0;out[@"metadata"]=Metadata74(&slide);
        if(strcmp(argv[1],"metadata")==0){out[@"primitive_calls"]=@0;}
        else{
            Need(strcmp(argv[1],"evaluate")==0,@"probe mode");
            From74 from=(From74)(uintptr_t)(0x1c59b581cull+slide);
            Scale74 scale=(Scale74)(uintptr_t)(0x1c5ba4b0cull+slide);
            To74 to=(To74)(uintptr_t)(0x1c59b575cull+slide);
            Flip74 flip=(Flip74)(uintptr_t)(0x1c5ba65d4ull+slide);
            NSDictionary*spec=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@(argv[2])]options:0 error:NULL];Need(spec!=nil,@"cases JSON");
            for(NSDictionary*c in spec[@"cases"]){@autoreleasepool{
                out[@"checkpoint"]=c[@"id"];CGRect input=R4(c[@"rect"]),bounds=R4(c[@"bounds"]);NSArray*s=c[@"scale"];
                Need(input.size.width>0&&input.size.height>0&&s.count==2&&[s[0]doubleValue]>0&&[s[1]doubleValue]>0,@"positive bounded finite fixture");
                PixelRect74 a=from(input,0),aBefore=a;CGRect acg=to(a);
                PixelRect74 b=scale(a,[s[0]doubleValue],[s[1]doubleValue],0),bBefore=b;
                CGRect bcg=to(b),f=flip(bcg,bounds);
                Need(memcmp(&a,&aBefore,sizeof(a))==0&&memcmp(&b,&bBefore,sizeof(b))==0,@"original primitive changed input");
                [(NSMutableArray*)out[@"rows"]addObject:@{@"case":c[@"id"],@"input_rect":RA(input),@"scale":s,@"bounds":RA(bounds),@"from_pixel_rect":PA74(a),@"from_CGRect":RA(acg),@"scaled_pixel_rect":PA74(b),@"scaled_CGRect":RA(bcg),@"flipped_CGRect":RA(f),@"integer_inputs_unchanged":@YES}];
            }}
            out[@"primitive_calls"]=@([(NSArray*)out[@"rows"]count]*5);
        }
        uint64_t fpcr=0;__asm__ volatile("mrs %0, fpcr":"=r"(fpcr));Need([out[@"metadata"][@"FPCR"]isEqual:Hex(fpcr)],@"FPCR changed");
        out[@"completed"]=@YES;out[@"checkpoint"]=@"complete";
    }@catch(NSException*e){out[@"completed"]=@NO;out[@"exception"]=e.reason?:e.name;rc=3;}
    NSError*err=nil;NSData*d=[NSJSONSerialization dataWithJSONObject:out options:NSJSONWritingPrettyPrinted error:&err];
    if(!d||![d writeToFile:@(argv[3])options:NSDataWritingWithoutOverwriting error:&err])return 4;return rc;
}}
