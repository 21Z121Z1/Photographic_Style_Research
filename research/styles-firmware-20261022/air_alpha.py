"""Narrow whole-module AIR comparison with explicit provenance exclusions.

This is a text alpha-equivalence check, not a cross-platform GPU certificate.
Only declared identified types and internal globals are renamed, bijectively
in declaration order. Layouts, constants, code, fast-math flags, initializers,
samplers, specialization/binding metadata, and metadata IDs remain intact.
Target triple and the llvm.ident producer string are separately recorded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

# Consume strings/comments atomically so names inside metadata string literals
# or source comments cannot accidentally be renamed.
SYMBOL = r'(?:"(?:[^"\\]|\\[0-9A-Fa-f]{2})*"|[-a-zA-Z$._0-9]+)'
TOKEN = re.compile(r'[%@]' + SYMBOL + r'|"(?:[^"\\]|\\[0-9A-Fa-f]{2})*"|;[^\n]*')


def canonicalize(text: str) -> tuple[str, dict]:
    types = re.findall(r'^(' + '%' + SYMBOL + r') = type ', text, re.M)
    globals_ = re.findall(r'^(' + '@' + SYMBOL + r') = internal\b', text, re.M)
    if len(set(types)) != len(types) or len(set(globals_)) != len(globals_):
        raise ValueError("Duplicate definitions cannot be alpha-renamed")
    mapping = {name: f'%"psr.type.{i}"' for i, name in enumerate(types)}
    mapping.update({name: f'@"psr.internal.{i}"' for i, name in enumerate(globals_)})
    # A source symbol may use the reserved spelling. Never allow collisions.
    if set(mapping.values()) & set(TOKEN.findall(text)):
        raise ValueError("Canonical spelling collides with a source symbol")
    target = re.findall(r'^target triple = "([^"]+)"$', text, re.M)
    if len(target) != 1:
        raise ValueError("Expected one target triple")
    ident_nodes = re.findall(r'^!llvm.ident = !\{!(\d+)\}$', text, re.M)
    if len(ident_nodes) != 1:
        raise ValueError("Expected one llvm.ident producer node")
    ident = re.compile(r'^!' + ident_nodes[0] + r' = !\{!"(Apple metal version [^"\n]+)"\}$', re.M)
    producer = ident.findall(text)
    if len(producer) != 1:
        raise ValueError("Unexpected producer node shape")
    # Only a comment containing llvm-dis's temporary path is discarded.
    text = re.sub(r'^; ModuleID = [^\n]*\n', '', text, count=1)
    text = re.sub(r'^target triple = "[^"]+"$', 'target triple = "<recorded-platform>"', text, count=1, flags=re.M)
    text = ident.sub('!' + ident_nodes[0] + ' = !{!"<recorded-compiler-producer>"}', text, count=1)
    text = TOKEN.sub(lambda m: mapping.get(m.group(), m.group()), text)
    return text, {"target_triple": target[0], "llvm_ident": producer[0],
                  "type_renames": {k: v for k, v in mapping.items() if k.startswith('%')},
                  "internal_global_renames": {k: v for k, v in mapping.items() if k.startswith('@')}}


def compare(scratch: Path, inventory: Path, output: Path) -> dict:
    data = json.loads(inventory.read_text())
    result = {"scope": __doc__, "input_inventory_sha256": hashlib.sha256(inventory.read_bytes()).hexdigest(),
              "ios_metallib_sha256": data["ios_reference"]["sha256"],
              "host_metallib_sha256": data["host_reference"]["sha256"], "module_pairs": [],
              "native_GPU_equivalence_verified": False, "camera_pipeline_equivalence_verified": False}
    pairs = {}
    for shared in data["shared_functions"]:
        # Compare only unambiguous one-to-one module/function associations.
        if len(shared["ios_indices"]) != 1 or len(shared["host_indices"]) != 1:
            continue
        a, b = shared['ios_indices'][0], shared['host_indices'][0]
        if (a, b) in pairs:
            pairs[a, b]['shared_functions'].append(shared['function'])
            continue
        at, am = canonicalize((scratch/'ios'/f'{a:04d}.ll.txt').read_text())
        bt, bm = canonicalize((scratch/'host'/f'{b:04d}.ll.txt').read_text())
        row = {"shared_functions": [shared['function']], "ios_index": a, "host_index": b,
                                  "ios_canonical_sha256": hashlib.sha256(at.encode()).hexdigest(),
                                  "host_canonical_sha256": hashlib.sha256(bt.encode()).hexdigest(),
                                  "whole_module_alpha_equal_except_recorded_provenance": at == bt,
                                  "ios_provenance_and_renames": am, "host_provenance_and_renames": bm}
        result['module_pairs'].append(row); pairs[a, b] = row
    result["compared_function_count"] = sum(len(r['shared_functions']) for r in pairs.values())
    result["alpha_equal_function_count"] = sum(len(r['shared_functions']) for r in pairs.values() if r["whole_module_alpha_equal_except_recorded_provenance"])
    # Several functions inhabit the same module; report unique module pairs too.
    result['unique_module_pairs'] = len(pairs)
    result['alpha_equal_module_pairs'] = sum(r['whole_module_alpha_equal_except_recorded_provenance'] for r in pairs.values())
    if output.exists(): raise FileExistsError(output)
    output.write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('scratch', type=Path); p.add_argument('inventory', type=Path); p.add_argument('output', type=Path)
    a = p.parse_args(); r = compare(a.scratch, a.inventory, a.output)
    print(json.dumps({k: r[k] for k in ['compared_function_count', 'alpha_equal_function_count', 'unique_module_pairs', 'alpha_equal_module_pairs']}))
