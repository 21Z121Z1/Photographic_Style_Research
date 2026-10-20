#pragma once
#import "native_common.h"

// Calls only the explicitly named SPI below. NSInvocation preserves struct ABI.
static id Call(id target, NSString *name, NSArray *args) {
    NSMethodSignature *signature = [target methodSignatureForSelector:NSSelectorFromString(name)];
    if (!signature || signature.numberOfArguments != args.count + 2)
        @throw [NSException exceptionWithName:@"SPIABI" reason:name userInfo:nil];
    NSInvocation *call = [NSInvocation invocationWithMethodSignature:signature];
    call.target = target; call.selector = NSSelectorFromString(name);
    for (NSUInteger i = 0; i < args.count; i++) {
        const char *type = [signature getArgumentTypeAtIndex:i + 2];
        while (*type && strchr("rnNoORV", *type)) type++;
        id value = args[i];
        if (*type == '@') { __unsafe_unretained id item = value == NSNull.null ? nil : value; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "Q")) { uint64_t item = [value unsignedLongLongValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "q")) { int64_t item = [value longLongValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "i")) { int item = [value intValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "I")) { unsigned item = [value unsignedIntValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "B")) { BOOL item = [value boolValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "f")) { float item = [value floatValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "d")) { double item = [value doubleValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, @encode(CGPoint))) { CGPoint item = [value pointValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, @encode(CGSize))) { CGSize item = [value sizeValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, @encode(CGRect))) { CGRect item = [value rectValue]; [call setArgument:&item atIndex:i + 2]; }
        else @throw [NSException exceptionWithName:@"SPIABI" reason:[name stringByAppendingFormat:@" unsupported argument %s", type] userInfo:nil];
    }
    [call invoke];
    const char *type = signature.methodReturnType;
    if (*type == '@' || *type == '#') { __unsafe_unretained id result = nil; [call getReturnValue:&result]; return result; }
    if (*type == 'v') return NSNull.null;
    if (!strcmp(type, "i")) { int result; [call getReturnValue:&result]; return @(result); }
    if (!strcmp(type, "Q")) { uint64_t result; [call getReturnValue:&result]; return @(result); }
    if (!strcmp(type, "B")) { BOOL result; [call getReturnValue:&result]; return @(result); }
    if (!strcmp(type, "f")) { float result; [call getReturnValue:&result]; return @(result); }
    if (!strcmp(type, "d")) { double result; [call getReturnValue:&result]; return @(result); }
    @throw [NSException exceptionWithName:@"SPIABI" reason:[name stringByAppendingFormat:@" unsupported return %s", type] userInfo:nil];
}

static id Make(NSString *name) { return Call([NSClassFromString(name) alloc], @"init", @[]); }

