#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#import <objc/message.h>
#import <mach-o/dyld.h>
#import <mach-o/loader.h>
#import <mach/mach.h>
#import <mach/mach_vm.h>
#import <dlfcn.h>
#include <ptrauth.h>
#include <math.h>

static void Need(BOOL b,NSString*s){if(!b)@throw[NSException exceptionWithName:@"S66"reason:s userInfo:nil];}
static uint32_t Bits(float v){uint32_t b;memcpy(&b,&v,4);return b;}
static id Value(float v){return isfinite(v)?@(v):isnan(v)?@"NaN":v>0?@"+Inf":@"-Inf";}
static NSString*Hex(uint64_t n){return[NSString stringWithFormat:@"0x%llx",(unsigned long long)n];}
static uint64_t IMPAddress(Method m){return(uint64_t)ptrauth_strip(method_getImplementation(m),ptrauth_key_function_pointer);}
static NSData*Read(uint64_t addr,NSUInteger n){NSMutableData*d=[NSMutableData dataWithLength:n];mach_vm_size_t got=0;Need(mach_vm_read_overwrite(mach_task_self(),addr,n,(mach_vm_address_t)d.mutableBytes,&got)==KERN_SUCCESS&&got==n,@"bounded VM read failed");return d;}
static NSDictionary*Stub(uint64_t unslid,intptr_t slide){uint32_t w[8];memcpy(w,Read(unslid+slide,32).bytes,32);NSMutableArray*words=[NSMutableArray new];for(int i=0;i<8;i++)[words addObject:Hex(w[i])];NSMutableDictionary*j=[@{@"unslid":Hex(unslid),@"words":words,@"selector_decoded":@NO}mutableCopy];if((w[0]&0x9f000000)==0x90000000){int64_t imm=(((w[0]>>5)&0x7ffff)<<2)|((w[0]>>29)&3);if(imm&(1<<20))imm-=1<<21;uint64_t page=((unslid+slide)&~0xfffull)+imm*4096;unsigned rd=w[0]&31,rn=(w[1]>>5)&31,rt=w[1]&31;SEL sel=NULL;if(rd==rn&&rt==1&&(w[1]&0xffc00000)==0x91000000)sel=(SEL)(page+((w[1]>>10)&0xfff));else if(rd==rn&&rt==1&&(w[1]&0xffc00000)==0xf9400000){uint64_t pointer=0;memcpy(&pointer,Read(page+(((w[1]>>10)&0xfff)*8),8).bytes,8);sel=(SEL)pointer;}if(sel&&sel_isMapped(sel)){j[@"selector"]=@(sel_getName(sel));j[@"selector_decoded"]=@YES;}}return j;}
static Method Signature(Class cls,BOOL classMethod,NSString*n,const char*ret,NSArray<NSString*>*args){SEL s=NSSelectorFromString(n);Method m=classMethod?class_getClassMethod(cls,s):class_getInstanceMethod(cls,s);Need(m!=NULL,n);NSMethodSignature*sig=[NSMethodSignature signatureWithObjCTypes:method_getTypeEncoding(m)];Need(sig.numberOfArguments==args.count+2&&strcmp(sig.methodReturnType,ret)==0,@"method return ABI");for(NSUInteger i=0;i<args.count;i++)Need(strcmp([sig getArgumentTypeAtIndex:i+2],args[i].UTF8String)==0,@"method argument ABI");return m;}
int main(int argc,char**argv){@autoreleasepool{if(argc!=2)return 2;NSMutableDictionary*out=[NSMutableDictionary new];int rc=0;@try{
 Need(dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",RTLD_NOW|RTLD_LOCAL)!=NULL,@"CMI dlopen");intptr_t slide=0;NSString*uuid=nil;
 for(uint32_t i=0;i<_dyld_image_count();i++)if(strstr(_dyld_get_image_name(i),"/CMImaging.framework/")){slide=_dyld_get_image_vmaddr_slide(i);const struct mach_header_64*h=(void*)_dyld_get_image_header(i);const uint8_t*p=(const uint8_t*)(h+1);for(uint32_t n=0;n<h->ncmds;n++){const struct load_command*c=(void*)p;if(c->cmd==LC_UUID)uuid=[[NSUUID alloc]initWithUUIDBytes:((const struct uuid_command*)c)->uuid].UUIDString;p+=c->cmdsize;}}
 Need([uuid caseInsensitiveCompare:@"3CCD434E-B1E0-3F14-8EF6-E29D58379BE8"]==NSOrderedSame,@"CMI UUID");out[@"CMI_UUID"]=uuid;out[@"native_CPU_scalar_only"]=@YES;out[@"Metal_PSO_or_camera_execution"]=@NO;
 NSMutableArray*stubs=[NSMutableArray new];for(NSNumber*a in @[@(0x23804d660ull),@(0x23804c4c0ull),@(0x23804c7b0ull),@(0x238040060ull)])[stubs addObject:Stub(a.unsignedLongLongValue,slide)];out[@"optimized_stubs"]=stubs;
 Class utils=NSClassFromString(@"CMISmartStyleUtilitiesV1"),styleClass=NSClassFromString(@"CMISmartStyleV1"),renderer=NSClassFromString(@"CMISmartStyleMetalRendererV1");Need(utils&&styleClass&&renderer,@"classes");
 NSMutableDictionary*offsets=[NSMutableDictionary new];for(NSString*n in @[@"_inputImageTexture",@"_inputImageThumbnailTexture",@"_inputLinearImageTexture"]){Ivar v=class_getInstanceVariable(renderer,n.UTF8String);Need(v!=NULL,@"ivar");offsets[n]=@{@"offset":@(ivar_getOffset(v)),@"encoding":@(ivar_getTypeEncoding(v))};}out[@"renderer_input_ivars"]=offsets;
 Method forward=Signature(utils,YES,@"adjustedGainMapHeadroomForStyle:originalHeadroom:","f",@[@"@",@"f"]),reverse=Signature(utils,YES,@"originalGainMapHeadroomFromStyle:currentHeadroom:","f",@[@"@",@"f"]),flag=Signature(utils,YES,@"isHDRGainMapHeadroomAdjusted:",@encode(BOOL),@[@"@"]);
 float(*fwd)(id,SEL,id,float)=(void*)method_getImplementation(forward);float(*inv)(id,SEL,id,float)=(void*)method_getImplementation(reverse);BOOL(*has)(id,SEL,id)=(void*)method_getImplementation(flag);
 out[@"ABIs"]=@{@"forward":@(method_getTypeEncoding(forward)),@"inverse":@(method_getTypeEncoding(reverse)),@"flag":@(method_getTypeEncoding(flag))};
 out[@"IMP_unslid"]=@{@"forward":Hex(IMPAddress(forward)-slide),@"inverse":Hex(IMPAddress(reverse)-slide),@"flag":Hex(IMPAddress(flag)-slide)};
 Need(IMPAddress(forward)-slide==0x2333c8994ull&&IMPAddress(reverse)-slide==0x2333c89fcull&&IMPAddress(flag)-slide==0x2333c8a64ull,@"original helper address mismatch");
 double exponents[2];memcpy(exponents,Read(0x233559bf8ull+slide,16).bytes,16);uint64_t exbits[2];memcpy(exbits,exponents,16);Need(isfinite(exponents[0])&&isfinite(exponents[1])&&exponents[0]>0&&exponents[1]>0,@"finite exponents");out[@"literal_exponents"]=@{@"forward":@(exponents[0]),@"inverse":@(exponents[1]),@"forward_bits":Hex(exbits[0]),@"inverse_bits":Hex(exbits[1]),@"unslid_addresses":@[@"0x233559bf8",@"0x233559c00"]};
 void*symbol=dlsym(RTLD_DEFAULT,"CMISmartStyleCastTypeLongGray");Need(symbol!=NULL,@"LongGray constant");__unsafe_unretained id longGray=nil;memcpy(&longGray,symbol,sizeof(longGray));Need([longGray isKindOfClass:NSString.class],@"cast type constant class");out[@"LongGray_constant"]=@{@"value":longGray,@"symbol_slot_unslid":Hex((uint64_t)symbol-slide)};
 Signature(styleClass,NO,@"setCastType:","v",@[@"@"]);Signature(styleClass,NO,@"setToneBias:","v",@[@"f"]);Signature(styleClass,NO,@"castType","@",@[]);for(NSString*n in @[@"toneBias",@"colorBias",@"castIntensity"])Signature(styleClass,NO,n,"f",@[]);
 NSMutableArray*rows=[NSMutableArray new];for(int which=0;which<2;which++)for(NSNumber*tone in @[@(-1.f),@(0.f),@(1.f)]){
   id style=[styleClass new];if(which)((void(*)(id,SEL,id))objc_msgSend)(style,NSSelectorFromString(@"setCastType:"),longGray);((void(*)(id,SEL,float))objc_msgSend)(style,NSSelectorFromString(@"setToneBias:"),tone.floatValue);id cast=((id(*)(id,SEL))objc_msgSend)(style,NSSelectorFromString(@"castType"));Need((cast==longGray)==which,@"cast factory branch mismatch");float intensity=((float(*)(id,SEL))objc_msgSend)(style,NSSelectorFromString(@"castIntensity")),colour=((float(*)(id,SEL))objc_msgSend)(style,NSSelectorFromString(@"colorBias"));
   for(NSNumber*value in @[@0.f,@.25f,@.5f,@1.f,@1.25f,@2.f,@4.f,@8.f,@16.f,@64.f]){float h=value.floatValue,a=fwd(utils,method_getName(forward),style,h),b=inv(utils,method_getName(reverse),style,a),single=inv(utils,method_getName(reverse),style,h);id after=((id(*)(id,SEL))objc_msgSend)(style,NSSelectorFromString(@"castType"));float afterTone=((float(*)(id,SEL))objc_msgSend)(style,NSSelectorFromString(@"toneBias")),afterIntensity=((float(*)(id,SEL))objc_msgSend)(style,NSSelectorFromString(@"castIntensity")),afterColour=((float(*)(id,SEL))objc_msgSend)(style,NSSelectorFromString(@"colorBias"));Need(after==cast&&Bits(afterTone)==Bits(tone.floatValue)&&Bits(afterIntensity)==Bits(intensity)&&Bits(afterColour)==Bits(colour),@"style input mutated");[rows addObject:@{@"style":which?@"LongGray":@"factory-default",@"actual_cast":cast?:NSNull.null,@"cast_is_LongGray_pointer":@(cast==longGray),@"tone":tone,@"input":value,@"forward":Value(a),@"inverse_of_forward":Value(b),@"inverse_direct":Value(single),@"input_bits":@(Bits(h)),@"forward_bits":@(Bits(a)),@"roundtrip_bits":@(Bits(b)),@"inverse_direct_bits":@(Bits(single)),@"flag_helper":@(has(utils,method_getName(flag),style)),@"style_fields_unchanged":@YES}];}
 }
 out[@"rows"]=rows;out[@"completed"]=@YES;
 }@catch(NSException*e){out[@"completed"]=@NO;out[@"exception"]=e.reason?:e.name;rc=3;}
 NSError*err=nil;NSData*d=[NSJSONSerialization dataWithJSONObject:out options:NSJSONWritingPrettyPrinted error:&err];if(!d||![d writeToFile:@(argv[1]) options:NSDataWritingWithoutOverwriting error:&err])return 4;return rc;
}}
