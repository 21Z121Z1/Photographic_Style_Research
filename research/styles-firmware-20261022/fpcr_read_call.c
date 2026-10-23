/* S33 read-only FPCR boundary. No FPCR writes or rounding-mode setters.
 * Calls the sealed exported f32 primitive once. The new wrapper owns FCVTs.
 */
#include <pthread.h>
#include <stdint.h>
#include <string.h>

typedef float (*sqrt_function)(float);
typedef union { uint16_t bits; _Float16 number; } half_bits;
typedef union { uint32_t bits; float number; } single_bits;

typedef struct {
    uint64_t fpcr_before, fpcr_after;
    uint64_t thread_before, thread_after;
    uint64_t self_before, self_after;
    uint32_t input_single_bits, output_single_bits;
    uint16_t input_half_bits, output_half_bits;
    uint32_t original_call_count;
    int32_t thread_query_before, thread_query_after;
} read_report;
_Static_assert(sizeof(read_report) == 72, "Bound report ABI must remain72 bytes");

__attribute__((noinline))
int psr_fpcr_read_call(sqrt_function function, uint16_t input, read_report *report) {
    if (!function || !report || input != 0x3880u) return -1;
    memset(report, 0, sizeof(*report));
    report->input_half_bits = input;
    report->thread_query_before = pthread_threadid_np(NULL, &report->thread_before);
    report->self_before = (uint64_t)(uintptr_t)pthread_self();
    if (report->thread_query_before != 0) return -2;
    volatile half_bits source = {.bits = input};
    uint64_t before, after;
    __asm__ volatile("mrs %0, fpcr" : "=r"(before) : : "memory");
    single_bits input_single = {.number = (float)source.number};
    single_bits output_single = {.number = function(input_single.number)};
    volatile half_bits narrowed = {.number = (_Float16)output_single.number};
    __asm__ volatile("mrs %0, fpcr" : "=r"(after) : : "memory");
    report->fpcr_before = before;
    report->fpcr_after = after;
    report->original_call_count = 1;
    report->input_single_bits = input_single.bits;
    report->output_single_bits = output_single.bits;
    report->output_half_bits = narrowed.bits;
    report->self_after = (uint64_t)(uintptr_t)pthread_self();
    report->thread_query_after = pthread_threadid_np(NULL, &report->thread_after);
    return report->thread_query_after == 0 ? 0 : -3;
}
