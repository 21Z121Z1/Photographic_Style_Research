#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#import <dlfcn.h>
#import <ptrauth.h>
#import <mach/mach.h>
#import <mach/mach_vm.h>
int main(int argc,char **argv) { @autoreleasepool {
    if(argc!=3) return 2;
    dlopen("/System/Library/PrivateFrameworks/PhotoImaging.framework/PhotoImaging",RTLD_NOW|RTLD_LOCAL);
    dlopen("/System/Library/PrivateFrameworks/NeutrinoCore.framework/NeutrinoCore",RTLD_NOW|RTLD_LOCAL);
    dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",RTLD_NOW|RTLD_LOCAL);
    Method m=class_getInstanceMethod(NSClassFromString(@"PISemanticStyleFilter"),NSSelectorFromString(@"outputImage"));
    intptr_t slide=(uintptr_t)ptrauth_strip(method_getImplementation(m),ptrauth_key_function_pointer)-0x1cbef1c78ULL;
    NSArray *addresses=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@(argv[1])] options:0 error:NULL];
    NSMutableDictionary *result=[NSMutableDictionary new];
    for(NSString *hex in addresses) {
        uintptr_t vm=strtoull(hex.UTF8String,NULL,16),pc=vm+slide;
        Dl_info info={0};dladdr((void *)pc,&info);
        NSMutableDictionary *row=[@{@"image":@(info.dli_fname ?: ""),@"nearest_symbol":@(info.dli_sname ?: "")} mutableCopy];
        uint32_t code[3]={0};mach_vm_size_t actual=0;if(mach_vm_read_overwrite(mach_task_self(),pc,12,(mach_vm_address_t)code,&actual)!=KERN_SUCCESS || actual!=12){result[hex]=row;continue;}
        // objc selector stubs in this cache use ADRP x1; ADD x1,x1; B msgSend.
        uint32_t a=code[0],b=code[1];
        if((a&0x9f00001f)==0x90000001 && (b&0xffc003ff)==0x91000021) {
            int64_t imm=(((int64_t)((a>>5)&0x7ffff))<<2)|((a>>29)&3);
            if(imm&(1<<20))imm-=(1<<21);
            uintptr_t pointer=(pc&~0xfffULL)+(imm<<12)+((b>>10)&0xfff);
            char name[512]={0};actual=0;if(mach_vm_read_overwrite(mach_task_self(),pointer,511,(mach_vm_address_t)name,&actual)!=KERN_SUCCESS)continue;
            NSString *selector=[[NSString alloc]initWithBytes:name length:strnlen(name,511) encoding:NSUTF8StringEncoding];
            if(selector)row[@"selector"]=selector;
        }
        result[hex]=row;
    }
    NSData *json=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL];
    [json writeToFile:@(argv[2]) atomically:YES];printf("Resolved %lu native call sites\n",(unsigned long)result.count);
}return 0;}
