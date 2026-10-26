/* A new Apple CPU reference. It does not load or impersonate the S25 image. */
#if !defined(__APPLE__) || !defined(__aarch64__)
#error "Apple arm64 is required"
#endif
#define _DARWIN_C_SOURCE 1
#include <dlfcn.h>
#include <mach-o/loader.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef float (*power_function)(float, float);
typedef union { uint16_t bits; _Float16 value; } half_value;
typedef union { uint32_t bits; float value; } single_value;
typedef struct {
    uint64_t before, after;
    uint32_t a, b, result;
    uint16_t half;
} power_observation;

__attribute__((noinline))
static power_observation probe_power(power_function function) {
    volatile half_value base = {.bits = 0x2b8f}, exponent = {.bits = 0x36aa};
    uint64_t before, after;
    __asm__ volatile("mrs %0, fpcr" : "=r"(before) : : "memory");
    single_value a = {.value = (float)base.value}, b = {.value = (float)exponent.value};
    single_value result = {.value = function(a.value, b.value)};
    volatile half_value half = {.value = (_Float16)result.value};
    __asm__ volatile("mrs %0, fpcr" : "=r"(after) : : "memory");
    return (power_observation){before, after, a.bits, b.bits, result.bits, half.bits};
}

__attribute__((noinline))
static void probe_root(uint16_t input, uint32_t *single, uint16_t *half,
                       uint64_t *before, uint64_t *after) {
    uint32_t in = input, out, narrowed;
    uint64_t fpcr0, fpcr1;
    __asm__ volatile(
        "mrs %0, fpcr\n"
        "fmov s0, %w4\n"
        "fcvt s0, h0\n"
        "fsqrt s0, s0\n"
        "fmov %w2, s0\n"
        "fcvt h1, s0\n"
        "fmov %w3, s1\n"
        "mrs %1, fpcr\n"
        : "=&r"(fpcr0), "=&r"(fpcr1), "=&r"(out), "=&r"(narrowed)
        : "r"(in) : "v0", "v1", "memory");
    *before = fpcr0;
    *after = fpcr1;
    *single = out;
    *half = (uint16_t)narrowed;
}

static int image_uuid(const void *base, char out[33]) {
    const struct mach_header_64 *h = base;
    if (!h || h->magic != MH_MAGIC_64 || h->sizeofcmds > 1024 * 1024) return -1;
    const unsigned char *p = (const unsigned char *)(h + 1), *end = p + h->sizeofcmds;
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

int main(void) {
    power_function power = (power_function)dlsym(RTLD_DEFAULT, "powf");
    Dl_info target;
    char uuid[33];
    uint64_t thread0 = 0, thread1 = 0;
    if (!power || !dladdr((const void *)power, &target) ||
        image_uuid(target.dli_fbase, uuid) || pthread_threadid_np(NULL, &thread0)) return 2;
    power_observation p = probe_power(power);
    printf("{\"schema\":\"psr-fresh-apple-cpu-v1\",\"target_uuid\":\"%s\",", uuid);
    const char *basename = strrchr(target.dli_fname, '/');
    printf("\"target_image\":\"%s\",\"target_symbol\":\"%s\",",
           basename ? basename+1 : target.dli_fname, target.dli_sname ? target.dli_sname : "unknown");
    printf("\"target_image_offset\":%llu,\"target_symbol_exact\":%s,",
           (unsigned long long)((uintptr_t)power-(uintptr_t)target.dli_fbase),
           target.dli_saddr == (void *)power ? "true" : "false");
    printf("\"power\":{\"input_half_bits\":[11151,13994],\"input_single_bits\":[%u,%u],"
           "\"output_single_bits\":%u,\"output_half_bits\":%u,\"fpcr_before\":%llu,\"fpcr_after\":%llu},",
           p.a, p.b, p.result, p.half, (unsigned long long)p.before, (unsigned long long)p.after);
    printf("\"sqrt_rows\":[");
    for (uint32_t input = 0x3401; input <= 0x3bff; ++input) {
        uint32_t single; uint16_t half; uint64_t before, after;
        probe_root((uint16_t)input, &single, &half, &before, &after);
        printf("%s[%u,%u,%u,%llu,%llu]", input == 0x3401 ? "" : ",", input, single, half,
               (unsigned long long)before, (unsigned long long)after);
    }
    if (pthread_threadid_np(NULL, &thread1)) return 3;
    printf("],\"thread_before\":%llu,\"thread_after\":%llu,\"pow_calls\":1,\"sqrt_instructions\":2047,"
           "\"historical_sealed_image_loaded\":false}\n", (unsigned long long)thread0, (unsigned long long)thread1);
    return 0;
}
