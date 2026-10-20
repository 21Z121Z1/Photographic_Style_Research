import lldb
import re


def target_label(target, process, address):
    """Resolve original shared-cache selector stubs without executing them."""
    error = lldb.SBError()
    regs = {}
    for instruction in target.ReadInstructions(target.ResolveLoadAddress(address), 6):
        pc = instruction.GetAddress().GetLoadAddress(target)
        word = instruction.GetData(target).GetUnsignedInt32(error, 0)
        if not error.Success():
            break
        if word & 0x9F000000 == 0x90000000:  # ADRP
            immediate = ((word >> 5) & 0x7FFFF) << 2 | ((word >> 29) & 3)
            if immediate & (1 << 20):
                immediate -= 1 << 21
            regs[word & 31] = (pc & ~4095) + (immediate << 12)
        elif word & 0xFF800000 == 0x91000000:  # ADD immediate, 64 bit
            source = (word >> 5) & 31
            if source in regs:
                regs[word & 31] = regs[source] + (((word >> 10) & 4095) << (12 if word & (1 << 22) else 0))
                if word & 31 == 1:
                    selector = process.ReadCStringFromMemory(regs[1], 1024, error)
                    if error.Success() and selector and all(32 <= ord(c) < 127 for c in selector):
                        return 'selector=' + selector
        elif word & 0xFFC00000 == 0xF9400000:  # LDR unsigned immediate, 64 bit
            source, dest = (word >> 5) & 31, word & 31
            if source not in regs:
                continue
            pointer = process.ReadPointerFromMemory(regs[source] + ((word >> 10) & 4095) * 8, error)
            if not error.Success():
                continue
            regs[dest] = pointer
            if dest == 1:
                selector = process.ReadCStringFromMemory(pointer, 1024, error)
                if error.Success() and selector and all(32 <= ord(c) < 127 for c in selector):
                    return 'selector=' + selector
            if dest == 16:
                symbol = target.ResolveLoadAddress(pointer).GetSymbol()
                if symbol.IsValid():
                    return symbol.GetName() or ''
    return ''


def original_disassembly(debugger, command, result, internal_dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    contexts = target.FindFunctions(command, lldb.eFunctionNameTypeFull)
    if not contexts.GetSize():
        result.AppendMessage('MISSING_SYMBOL ' + command)
        return
    for context in contexts:
        symbol = context.GetSymbol()
        function = context.GetFunction()
        instructions = function.GetInstructions(target) if function.IsValid() else symbol.GetInstructions(target)
        result.AppendMessage('ORIGINAL_METHOD ' + command)
        for instruction in instructions:
            pc = instruction.GetAddress().GetLoadAddress(target)
            mnemonic = instruction.GetMnemonic(target)
            operands = instruction.GetOperands(target)
            comment = instruction.GetComment(target) or ''
            match = re.search(r'0x[0-9a-fA-F]+', operands)
            if mnemonic in ('bl', 'b') and match:
                label = target_label(target, process, int(match.group(0), 16))
                if label:
                    comment += ' ' + label
            result.AppendMessage(f'{pc:#x}: {mnemonic:8} {operands:45} ; {comment}')


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f disassemble.original_disassembly original-disassembly')
