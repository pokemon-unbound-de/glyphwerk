# Game Profile Schema (`schema_version: 1`)

All ROM-specific offsets live in JSON profiles under `profiles/`. Never hardcode project offsets in Python modules.

## Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `schema_version` | `int` | Yes | Must be `1`. |
| `profile_id` | `string` | Yes | Machine-readable profile identifier (e.g. `firered_bpre_rev0`). |
| `title` | `string` | No | Human-readable label. |
| `rom_base_addr` | `hex/int` | No | GBA ROM bus mapping base (default `"0x08000000"`). |
| `rom_max_size` | `int` | No | Maximum ROM size in bytes (`16777216` for 16 MB, `33554432` for 32 MB). |
| `header_guard_end` | `hex/int` | No | End of protected GBA ROM header (default `"0x00000200"`). |
| `strcpy_addr` | `hex/int \| null` | No | ROM address of `libc strcpy` for `glyphwerk.gates.strcpy_safety`. |
| `font_widths_table` | `hex/int \| null` | No | Offset of font glyph advance widths table in base ROM. |
| `free_space.fill_byte` | `hex/int` | No | Free-space fill byte (default `"0xFF"`). |
| `free_space.min_run_bytes` | `int` | No | Minimum contiguous run length eligible for pool allocation (default `64`). |
| `free_space.terminator_guard_bytes` | `int` | No | Leading bytes skipped at the start of every `0xFF` run (default `2`, protects preceding string's `0xFF` terminator). |
| `free_space.reserved_ranges` | `[[hex, hex], ...]` | No | Explicit `[start, end)` intervals excluded from pool allocation. |
| `script_banks` | `[[hex, hex], ...]` | No | ROM `[start, end)` intervals scanned for unaligned XSE script text pointers. |
| `windows` | `object` | No | Named UI box specs: `{"max_line_px": int, "max_lines": int}`. |
| `buffer_max_px` | `object` | No | Worst-case pixel expansion per buffer ID (`"FD01"`, `"FD06"`, `"default"`). |
| `wram_bpre` | `object` | No | WRAM/SaveBlock addresses consumed by `glyphwerk/bot/explorer.lua`. |
| `rom_game_code` | `string` | No | 4-character game code from the ROM header at `0xAC` (e.g. `"BPRE"`). |
| `display.width_px`, `display.height_px`, `display.frame_rate_hz` | `int`, `int`, `float` | No | Screen size and refresh rate of the console (GBA: 240 × 160 at 59.7275 Hz). |

Machine-specific settings (emulator path, runtime folder, start state, capture size) do not belong in a profile, which is public and describes the game. Pass them as environment variables instead.

See [`profiles/firered_bpre.json`](../profiles/firered_bpre.json) and [`profiles/cfru_template.json`](../profiles/cfru_template.json) for complete examples.
