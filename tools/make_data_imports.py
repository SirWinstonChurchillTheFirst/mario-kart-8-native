#!/usr/bin/env python3
"""Writes the data-imports map for a rebased RPL module from YOUR OWN game dump.

usage: make_data_imports.py MODULE.rpl DATA_REBASE_HEX [OUT]
  e.g. make_data_imports.py "<game>/code/mvplayer.rpl" 00300000 data-imports.map

One line per data export: "<module> <name> <rebased address hex>". The rebase must match the data
offset given to the recompiler in CAFE_RPL_REBASE (code,data) when the module was translated.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rpxinfo  # noqa: E402

path, rebase = sys.argv[1], int(sys.argv[2], 16)
out = sys.argv[3] if len(sys.argv) > 3 else None
module = os.path.splitext(os.path.basename(path))[0]
_, secs, data = rpxinfo.load(path)
lines = []
for s in secs:
    if s["type"] != 0x80000001:
        continue
    d = data(s)
    count, _sig = struct.unpack_from(">II", d, 0)
    for k in range(count):
        value, noff = struct.unpack_from(">II", d, 8 + k * 8)
        if value < 0x10000000:  # code export (.fexports): bound by the module loader, not by this map
            continue
        noff &= 0x7FFFFFFF
        name = d[noff:d.index(b"\0", noff)].decode()
        lines.append(f"{module} {name} {value + rebase:08X}")
text = "\n".join(lines) + "\n"
if out:
    with open(out, "w", newline="\n") as f:
        f.write(text)
else:
    sys.stdout.write(text)
