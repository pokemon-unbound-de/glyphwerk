#!/usr/bin/env python3
"""Self-contained synthetic 64-KB ROM localization & gate demo (zero real ROMs required)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from glyphwerk.codec.pcs import decode, encode  # noqa: E402
from glyphwerk.codec.width import lint_text  # noqa: E402
from glyphwerk.demo_data import build_synthetic_rom  # noqa: E402
from glyphwerk.gates.gfx_pointers import check_gfx_pointers  # noqa: E402
from glyphwerk.gates.rom_header import check_rom_header_pointers  # noqa: E402
from glyphwerk.gates.strcpy_safety import check_strcpy_safety  # noqa: E402
from glyphwerk.porter.dex_wrap import wrap_balanced  # noqa: E402
from glyphwerk.porter.tables import TableEntry, apply_table_entries  # noqa: E402
from glyphwerk.rom.pointers import find_all_pointers  # noqa: E402
from glyphwerk.rom.relocate import PoolAllocator, graphic_lock_ranges, relocate_string  # noqa: E402


def main() -> int:
    layout = build_synthetic_rom()
    base = bytes(layout.rom)
    patched = bytearray(base)

    # 1. Fixed-stride table patch (in-place with EN guard)
    tbl_rep = apply_table_entries(
        patched,
        [
            TableEntry(layout.table_base, 12, "CHERI", "AMRENA"),
            TableEntry(layout.table_base + 12, 12, "ORAN", "SINEL"),
            TableEntry(layout.table_base + 24, 12, "LUM", "PRUNUS"),
        ],
    )
    assert tbl_rep.ok, tbl_rep.errors

    # 2. Relocate dialog string across both 4B-aligned and unaligned XSE pointers
    new_text = "Willkommen, [#FD01]!\\nBereit fuer das Abenteuer?"
    width_rep = lint_text(new_text, max_line_px=208, max_lines=2)
    assert width_rep.ok, width_rep

    alloc = PoolAllocator(patched, min_run=64)
    locks = graphic_lock_ranges(base)
    ptrs = [h.offset for h in find_all_pointers(base, layout.dialog_str_offset)]
    tr_bytes, bad = encode(new_text, terminate=True)
    assert not bad
    rel = relocate_string(patched, layout.dialog_str_offset, tr_bytes, ptrs, alloc, gfx_locks=locks)

    # 3. Balanced Pokédex wrap example
    wrapped = wrap_balanced(
        "Dieses Wesen wandert bei Vollmond über hohe Bergkämme und\\n"
        "sammelt leuchtende Kristalle tief im Tal.",
        max_line_px=230,
        max_lines=3,
    )
    assert wrapped.ok and wrapped.changed

    # 4. Run all binary gates
    assert check_gfx_pointers(base, patched) == []
    assert check_rom_header_pointers(base, patched) == []
    assert check_strcpy_safety(base, patched, strcpy_addr=layout.strcpy_addr) == []

    print(
        f"DEMO GREEN: table_applied={tbl_rep.applied}, ptrs_updated={len(rel.pointers_updated)}, "
        f"reloc_dst=0x{rel.target_offset:05X}, readback={decode(patched[rel.target_offset:rel.target_offset+64])!r}, "
        f"dex_wrap_widths={wrapped.line_widths}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
