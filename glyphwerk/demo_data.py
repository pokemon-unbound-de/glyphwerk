"""Deterministic synthetic 64-KB GBA ROM used by the demo and the test suite.

Every byte is generated here from scratch: no copyrighted ROM data, no game text and
no real ROM offsets. The layout exercises every Glyphwerk module (tables, Thumb code,
strcpy calls, aligned and unaligned script pointers, LZ77 graphics and a free pool).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

from glyphwerk.codec.pcs import encode
from glyphwerk.gfx.lz77 import compress_lz77

__all__ = ["ROM_BASE", "SyntheticRomLayout", "build_synthetic_rom"]

ROM_BASE = 0x08000000


def _encode_thumb_bl(src_offset: int, dst_offset: int) -> bytes:
    """Encode a 32-bit Thumb BL instruction from ``src_offset`` to ``dst_offset``."""
    delta = dst_offset - (src_offset + 4)
    assert -(1 << 22) <= delta < (1 << 22) and (delta & 1) == 0
    if delta < 0:
        delta += 1 << 23
    h1 = 0xF000 | ((delta >> 12) & 0x7FF)
    h2 = 0xF800 | ((delta >> 1) & 0x7FF)
    return struct.pack("<HH", h1, h2)


@dataclass
class SyntheticRomLayout:
    rom: bytearray
    header_ptr_site: int
    table_base: int
    table_stride: int
    table_literal_site: int
    strcpy_addr: int
    strcpy_bl_site: int
    strcpy_str_offset: int
    dialog_str_offset: int
    dialog_aligned_ptr: int
    dialog_xse_ptr: int
    lz77_ptr_site: int
    lz77_offset: int
    lz77_len: int
    free_pool_start: int
    free_pool_end: int


def build_synthetic_rom() -> SyntheticRomLayout:
    """Create a deterministic 64-KB synthetic ROM exercising every Glyphwerk module."""
    rom = bytearray(0x10000)  # zero-initialized 64 KB

    # 1. Synthetic ROM header (0x0000..0x01FF) + header-referencing code pointer @ 0x0400
    rom[0xA0:0xAC] = b"SYNTH_DEMO01"
    header_ptr_site = 0x0400
    struct.pack_into("<I", rom, header_ptr_site, ROM_BASE + 0x00A0)

    # 2. Fixed-stride table @ 0x1000 (stride 12 B)
    table_base = 0x1000
    table_stride = 12
    for idx, label in enumerate(("CHERI", "ORAN", "LUM")):
        raw, bad = encode(label, terminate=True)
        assert not bad
        slot_off = table_base + idx * table_stride
        rom[slot_off : slot_off + table_stride] = raw + b"\xFF" * (table_stride - len(raw))

    # 3. Thumb function @ 0x2000 loading table_base literal @ 0x2010 and adding scaled index:
    #    0x2000: lsls r0, r0, #2       (0x0080)
    #    0x2002: ldr  r1, [pc, #0x08]  (0x4902) -> ((0x2002+4)&~3) + 8 = 0x2004 + 8 = 0x200C!
    #    Let's place literal cleanly at 0x200C!
    #    0x2004: adds r0, r1, r0       (0x1808 -> rd=0, rn=1, rm=0: 0001100 000 001 000 = 0x1808)
    #    0x2006: bx   lr               (0x4770)
    table_literal_site = 0x200C
    struct.pack_into("<HHHH", rom, 0x2000, 0x0080, 0x4902, 0x1808, 0x4770)
    struct.pack_into("<I", rom, table_literal_site, ROM_BASE + table_base)

    # 4. Thumb function @ 0x2100 calling libc strcpy (@ 0x08002800) with literal PCS string @ 0x3000
    #    0x2100: ldr r1, [pc, #0x08] (0x4902) -> ((0x2100+4)&~3) + 8 = 0x210C
    #    0x2102: bl  0x2800
    #    0x2106: bx  lr              (0x4770)
    strcpy_addr = ROM_BASE + 0x2800
    strcpy_bl_site = 0x2102
    strcpy_str_offset = 0x3000
    struct.pack_into("<H", rom, 0x2100, 0x4902)
    rom[0x2102:0x2106] = _encode_thumb_bl(0x2102, 0x2800)
    struct.pack_into("<H", rom, 0x2106, 0x4770)
    struct.pack_into("<I", rom, 0x210C, ROM_BASE + strcpy_str_offset)
    sc_raw, _ = encode("Go back now", terminate=True)  # First 0x00 space at offset +2 (len=3)
    rom[strcpy_str_offset : strcpy_str_offset + len(sc_raw)] = sc_raw

    # 5. Dialog string @ 0x3100 referenced by BOTH aligned 4B pointer (0x5040) and unaligned XSE (0x5003)
    dialog_str_offset = 0x3100
    dlg_raw, _ = encode("Hello [#FD01]!", terminate=True)
    rom[dialog_str_offset : dialog_str_offset + len(dlg_raw)] = dlg_raw
    dialog_aligned_ptr = 0x5040
    struct.pack_into("<I", rom, dialog_aligned_ptr, ROM_BASE + dialog_str_offset)
    # XSE script: 0x5001: 0x0F 0x00 <4B ptr @ 0x5003>
    dialog_xse_ptr = 0x5003
    rom[0x5001] = 0x0F
    rom[0x5002] = 0x00
    struct.pack_into("<I", rom, dialog_xse_ptr, ROM_BASE + dialog_str_offset)

    # 6. Referenced GBA BIOS 0x10 LZ77 graphic payload @ 0x4000 (pointed to by 0x0420)
    #    Embed a literal 4B pattern 0x08003100 inside uncompressed bytes so it appears in compressed stream
    gfx_raw = bytearray(128)
    for i in range(128):
        gfx_raw[i] = (i * 7 + 3) & 0xFF
    struct.pack_into("<I", gfx_raw, 16, ROM_BASE + dialog_str_offset)
    lz_payload = compress_lz77(gfx_raw)
    lz77_offset = 0x4000
    lz77_ptr_site = 0x0420
    rom[lz77_offset : lz77_offset + len(lz_payload)] = lz_payload
    struct.pack_into("<I", rom, lz77_ptr_site, ROM_BASE + lz77_offset)

    # 7. Free 0xFF pool @ 0xC000..0xE000 (immediately after a preceding string terminator at 0xC000)
    free_pool_start = 0xC000
    free_pool_end = 0xE000
    prev_str, _ = encode("Prev", terminate=False)
    rom[free_pool_start - len(prev_str) : free_pool_start] = prev_str
    rom[free_pool_start:free_pool_end] = b"\xFF" * (free_pool_end - free_pool_start)

    return SyntheticRomLayout(
        rom=rom,
        header_ptr_site=header_ptr_site,
        table_base=table_base,
        table_stride=table_stride,
        table_literal_site=table_literal_site,
        strcpy_addr=strcpy_addr,
        strcpy_bl_site=strcpy_bl_site,
        strcpy_str_offset=strcpy_str_offset,
        dialog_str_offset=dialog_str_offset,
        dialog_aligned_ptr=dialog_aligned_ptr,
        dialog_xse_ptr=dialog_xse_ptr,
        lz77_ptr_site=lz77_ptr_site,
        lz77_offset=lz77_offset,
        lz77_len=len(lz_payload),
        free_pool_start=free_pool_start,
        free_pool_end=free_pool_end,
    )
