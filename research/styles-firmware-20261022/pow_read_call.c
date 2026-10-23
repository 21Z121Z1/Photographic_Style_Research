/* One current Apple arm64 CPU call through the SEALED shim, never a replacement
 * pow implementation. The driver validates the original file SHA before load.
 * Neither this file nor the shim is a GPU or complete pipeline oracle. */
#if !defined(__APPLE__) || !defined(__aarch64__)
#error "This collector requires Apple arm64; no substitute backend is allowed"
#endif
#define _DARWIN_C_SOURCE 1
#include <dlfcn.h>
#include <mach-o/loader.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef float (*pow_function)(float, float);
typedef union { uint16_t bits; _Float16 number; } half_bits;
typedef union { uint32_t bits; float number; } single_bits;
typedef struct {
    uint64_t fpcr_before, fpcr_after, thread_before, thread_after;
    uint64_t self_before, self_after;
    uint32_t base_single_bits, exponent_single_bits, output_single_bits;
    uint16_t base_half_bits, exponent_half_bits, output_half_bits;
    uint32_t original_call_count;
    int32_t thread_query_before, thread_query_after;
} pow_report;

__attribute__((noinline))
int psr_pow_read_call(pow_function function, pow_report *r) {
    if (!function || !r) return -1;
    memset(r, 0, sizeof(*r));
    r->base_half_bits = 0x2b8f;
    r->exponent_half_bits = 0x36aa;
    r->thread_query_before = pthread_threadid_np(NULL, &r->thread_before);
    r->self_before = (uint64_t)(uintptr_t)pthread_self();
    if (r->thread_query_before) return -2;
    volatile half_bits base = {.bits = 0x2b8f}, exponent = {.bits = 0x36aa};
    uint64_t before, after;
    __asm__ volatile("mrs %0, fpcr" : "=r"(before) : : "memory");
    single_bits a = {.number = (float)base.number};
    single_bits b = {.number = (float)exponent.number};
    single_bits out = {.number = function(a.number, b.number)};
    volatile half_bits narrowed = {.number = (_Float16)out.number};
    __asm__ volatile("mrs %0, fpcr" : "=r"(after) : : "memory");
    r->fpcr_before = before;
    r->fpcr_after = after;
    r->base_single_bits = a.bits;
    r->exponent_single_bits = b.bits;
    r->output_single_bits = out.bits;
    r->output_half_bits = narrowed.bits;
    r->original_call_count = 1;
    r->self_after = (uint64_t)(uintptr_t)pthread_self();
    r->thread_query_after = pthread_threadid_np(NULL, &r->thread_after);
    return r->thread_query_after ? -3 : 0;
}

static int image_uuid(const void *base, char out[33]) {
    const struct mach_header_64 *h = base;
    if (!h || h->magic != MH_MAGIC_64 || h->sizeofcmds > 1024 * 1024) return -1;
    const unsigned char *p = (const unsigned char *)(h + 1);
    const unsigned char *end = p + h->sizeofcmds;
    unsigned found = 0;
    for (uint32_t i = 0; i < h->ncmds; ++i) {
        if ((size_t)(end - p) < sizeof(struct load_command)) return -1;
        const struct load_command *c = (const struct load_command *)p;
        if (c->cmdsize < sizeof(*c) || c->cmdsize > (size_t)(end - p)) return -1;
        if (c->cmd == LC_UUID) {
            if (c->cmdsize != sizeof(struct uuid_command) || ++found != 1) return -1;
            const struct uuid_command *u = (const struct uuid_command *)p;
            for (unsigned j = 0; j < 16; ++j) snprintf(out + 2*j, 3, "%02x", u->uuid[j]);
        }
        p += c->cmdsize;
    }
    return found == 1 && p == end ? 0 : -1;
}

/* Reject unsupported/authenticated stubs. No dlsym("powf") fallback exists. */
static int got_slot(uintptr_t base, uintptr_t *slot) {
    uintptr_t branch_address = base + 0x15904u;
    uint32_t tail = *(const uint32_t *)branch_address;
    if ((tail & 0xfc000000u) != 0x14000000u) return -1;
    int64_t imm = (int64_t)(tail & 0x03ffffffu);
    if (imm & (1 << 25)) imm -= (1 << 26);
    uintptr_t stub = branch_address + (uintptr_t)(imm * 4);
    if (stub != base + 0x16244u) return -1;
    const uint32_t *s = (const uint32_t *)stub;
    if ((s[0] & 0x9f00001fu) != 0x90000010u ||
        (s[1] & 0xffc003ffu) != 0xf9400210u || s[2] != 0xd61f0200u) return -1;
    int64_t page = (int64_t)(((s[0] >> 5) & 0x7ffffu) << 2) | ((s[0] >> 29) & 3u);
    if (page & (1 << 20)) page -= (1 << 21);
    *slot = (stub & ~(uintptr_t)4095) + (uintptr_t)(page * 4096) + ((s[1] >> 10) & 0xfffu) * 8;
    return 0;
}

/* Output is deliberately line-oriented integers/UUIDs, with no private paths or
 * executable bytes. Full paths and command logs remain in the private run dir. */
int main(int argc, char **argv) {
    if (argc != 3) return 10;
    char *end = NULL;
    unsigned long long entry = strtoull(argv[2], &end, 10);
    if (!end || *end || entry > 0x15904u || entry < 0x15904u - 64u || entry % 4) return 10;
    void *library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (!library) { fputs("sealed image load failed\n", stderr); return 11; }
    pow_function f = (pow_function)dlsym(library, "psr_pow_scalar");
    Dl_info source, target;
    if (!f || !dladdr((void *)f, &source) || source.dli_saddr != (void *)f ||
        (uintptr_t)f - (uintptr_t)source.dli_fbase != entry) return 12;
    uintptr_t slot;
    if (got_slot((uintptr_t)source.dli_fbase, &slot)) return 13;
    uintptr_t before = *(const uintptr_t *)slot;
    if (!before || !dladdr((void *)before, &target)) return 14;
    char source_uuid[33], target_uuid[33];
    if (image_uuid(source.dli_fbase, source_uuid) || image_uuid(target.dli_fbase, target_uuid)) return 15;
    pow_report r;
    int rc = psr_pow_read_call(f, &r);
    uintptr_t after = *(const uintptr_t *)slot;
    printf("source_uuid %s\ntarget_uuid %s\n", source_uuid, target_uuid);
    printf("target_symbol %s\n", target.dli_sname ? target.dli_sname : "unknown");
    const char *path = target.dli_fname ? strrchr(target.dli_fname, '/') : NULL;
    printf("target_image_basename %s\n", path ? path + 1 : "unknown");
    printf("target_symbol_exact %u\n", target.dli_saddr == (void *)before);
    printf("target_image_offset %llu\n", (unsigned long long)(before - (uintptr_t)target.dli_fbase));
    printf("got_image_offset %llu\ngot_stable %u\n", (unsigned long long)(slot - (uintptr_t)source.dli_fbase), before == after);
    printf("native_return_code %d\noriginal_call_count %u\n", rc, r.original_call_count);
    printf("fpcr_before %llu\nfpcr_after %llu\n", (unsigned long long)r.fpcr_before, (unsigned long long)r.fpcr_after);
    printf("thread_before %llu\nthread_after %llu\n", (unsigned long long)r.thread_before, (unsigned long long)r.thread_after);
    printf("self_equal %u\nquery_before %d\nquery_after %d\n", r.self_before == r.self_after, r.thread_query_before, r.thread_query_after);
    printf("base_half_bits %u\nexponent_half_bits %u\n", r.base_half_bits, r.exponent_half_bits);
    printf("base_single_bits %u\nexponent_single_bits %u\n", r.base_single_bits, r.exponent_single_bits);
    printf("output_single_bits %u\noutput_half_bits %u\n", r.output_single_bits, r.output_half_bits);
    return rc ? 16 : 0;
}
