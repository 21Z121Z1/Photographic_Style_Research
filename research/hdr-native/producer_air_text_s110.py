"""Isolated LLVM parsing of one ephemeral AIR module; text output only."""
from pathlib import Path
import sys
sys.path.insert(0,sys.argv[1])
import llvmlite.binding as llvm
module=llvm.parse_bitcode(Path(sys.argv[2]).read_bytes())
Path(sys.argv[3]).write_text(str(module))
