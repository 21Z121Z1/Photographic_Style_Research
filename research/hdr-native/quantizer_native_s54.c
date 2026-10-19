#include <stdint.h>
#include <stdio.h>
#include <string.h>

#if !defined(__aarch64__)
#error "This probe requires native AArch64"
#endif

static void quantize(uint32_t input, uint32_t *minimum, uint32_t *maximum,
                     uint32_t *code, uint64_t *flags) {
    uint32_t a,b,c,one=0x3f800000u,scale=0x477fff00u;
    uint64_t f;
    __asm__ volatile("msr fpsr, xzr\n\t"
        "fmov s0, %w[one]\n\t"
        "fmov s1, wzr\n\t"
        "fmov s8, %w[scale]\n\t"
        "fmov s2, %w[in]\n\t"
        "fminnm s2, s2, s0\n\t"
        "fmov %w[a], s2\n\t"
        "fmaxnm s2, s2, s1\n\t"
        "fmov %w[b], s2\n\t"
        "fmul s2, s2, s8\n\t"
        "frintm s2, s2\n\t"
        "fcvtzs s2, s2\n\t"
        "fmov %w[c], s2\n\t"
        "mrs %[f], fpsr\n\t"
        : [a]"=&r"(a),[b]"=&r"(b),[c]"=&r"(c),[f]"=&r"(f)
        : [in]"r"(input),[one]"r"(one),[scale]"r"(scale)
        : "v0","v1","v2","v8","memory");
    *minimum=a;*maximum=b;*code=c;*flags=f;
}

int main(int argc,char **argv) {
    if(argc!=2)return 2;
    FILE *out=fopen(argv[1],"wx");if(!out)return 3;
    const uint32_t inputs[]={0xff800000,0xbf800000,0x80000000,0,1,0x3f800000,
                            0x40000000,0x7f800000,0x7fc00001,0xffc00001,
                            0x7f800001,0xff800001};
    uint64_t oldFPCR,oldFPSR,newFPCR;
    __asm__ volatile("mrs %0, fpcr\n\tmrs %1, fpsr":"=r"(oldFPCR),"=r"(oldFPSR));
    __asm__ volatile("msr fpcr, xzr\n\tisb":::"memory");
    __asm__ volatile("mrs %0, fpcr":"=r"(newFPCR));
    fprintf(out,"{\"native_AArch64\":true,\"FPCR\":%llu,\"initial_FPCR\":%llu,\"rows\":[",
            (unsigned long long)newFPCR,(unsigned long long)oldFPCR);
    for(unsigned i=0;i<sizeof(inputs)/sizeof(inputs[0]);i++) {
        uint32_t a,b,c;uint64_t flags;quantize(inputs[i],&a,&b,&c,&flags);
        fprintf(out,"%s{\"input_bits\":\"%08x\",\"after_min_bits\":\"%08x\",\"after_max_bits\":\"%08x\",\"code\":%u,\"FPSR\":%llu}",
                i?",":"",inputs[i],a,b,c,(unsigned long long)flags);
    }
    fprintf(out,"]}\n");
    __asm__ volatile("msr fpcr, %0\n\tmsr fpsr, %1\n\tisb"::"r"(oldFPCR),"r"(oldFPSR):"memory");
    return fclose(out)==0?0:4;
}
