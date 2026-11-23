# Mario Kart 8 (Wii U): native build, work in progress

An attempt to run the Wii U game as a native Linux (and Windows) program by static recompilation: the game's
PowerPC code is translated to C++ ahead of time and runs on a reimplementation of the Wii U's system libraries.
No emulator.

> **No game files are included.** You need your own dump of the game (Europe), unpacked to `code/`, `content/`,
> `meta/`. The translated C++ and the program built from it contain the game's code: do not share them.
> Not affiliated with or endorsed by Nintendo.

## Status (23 November 2026): races run at 59-60 frames/s on a Batocera console, menu videos play

| Step | State |
| --- | --- |
| Title, menus, cup/character/kart select | works (PC and console) |
| A race (Mario Kart Stadium) with the other racers | works: lit track, karts, drivers, HUD, sound |
| Speed | console (Ryzen 3 4350GE, Vega 6): 58-60 frames/s in the race, ~45 while loading; CPU 67 C, GPU 60 C |
| Menu preview videos | work where FFmpeg's `libavcodec` (.so.61 or .58) is installed: the runtime's H.264 decoder interface (`port/os_extra.cpp`, `patch_h264.py`) hands the stream to it at run time; without it the frames stay black (sound plays) |
| Online, Mario Kart TV upload | not available |

**Miis.** The game asks for the Wii U's Mii resources (system title `0005001B-10056000`). They are **not** part of
the game and **not** included here: point `CAFE_SYS_DIR` at a Cemu-style `mlc01/sys` folder holding
`title/0005001b/10056000/content/` from your own Wii U.

## What it took

- **Two modules.** Mario Kart 8 loads its own library `mvplayer.rpl` (the video player). It is translated separately,
  rebased to free addresses (`patch_rpl_rebase.py`, `module_rename.py`) and loaded, bound and started by
  `port/modules.cpp` (`patch_modules.py`, `patch_mblock_size.py`); `tools/make_data_imports.py` writes the map that
  resolves the game's data imports from it (generated from your own `mvplayer.rpl`, not included).
- **Black picture, three causes:**
  - the GPU saw guest memory only up to the first hole, and the module's data left a hole before the heaps
    (`patch_import_gaps.py`);
  - the final colour grading reads an 8x8x8 3D table the game draws once per race load, eight slices in one draw.
    The runtime ignored the slice of a colour buffer and dropped draws whose shaders were still compiling
    (`patch_slice_targets.py`, `patch_slice_levels.py`, `patch_wait_compile.py`); the same made the drivers' lighting
    cubes (six faces per draw) appear;
  - an invalid cube view for a 48-face cube texture (`patch_cube_view.py`).
- **Speed on the console.** The game creates over 4000 render targets; every texture bind searched them all
  (9-14 frames/s). An address index fixes that (`patch_target_index.py`).
- **Menu videos.** `mvplayer.rpl` drives the system's `h264` library (`H264DEC*`); `port/os_extra.cpp` implements it
  and decodes with `libavcodec` loaded at run time (`CAFE_H264=0` / `CAFE_H264_DECODE=0` turn it off).
- Lock-free lists need a real `lwarx`/`stwcx.` reservation (`patch_reservation.py`, found with Mario & Sonic Rio 2016).

## What is here

This repository holds only what was added for this game, on top of
[Smash 4 PC](https://github.com/josiahg2502-glitch/Smash4PC) at `f145e7f` (MIT), which is built on
[Tekken Tag 2 Ultimate Edition](https://github.com/Petexy/Tekken-Tag-2-Ultimate-Edition)'s cafe-recomp and
Wii U runtime by Petexy (MIT). All credit for the recompiler and the runtime goes to them.

- `port/upstream-local.patch`: all changes to that runtime and recompiler; `port/patch_*.py` are the scripts that made
  them, each with a note on what and why.
- `port/game_main.cpp`, `port/os_extra.cpp`, `port/modules.cpp`, `port/netplay_none.cpp`: entry program, extra system
  functions, the module loader, a stand-in for the Windows-only netplay part.
- `tools/`: build and test helpers (`win_build.sh`, `run_gpu.sh`, `console_test.sh`, ...); `console/`: the Batocera
  launcher and deploy script.

Build outline (Linux): translate `mvplayer.rpl` with `CAFE_RPL_REBASE=06000000,00300000 CAFE_DATA_IMPORT_FIRST=32`,
rename its tables with `module_rename.py`, write the map with
`tools/make_data_imports.py <game>/code/mvplayer.rpl 00300000 mk8-data-imports.map`, translate `Turbo.rpx` with
`CAFE_DATA_IMPORT_MAP=mk8-data-imports.map`,
configure with `-DGAME_MODULE_DIRS=<module folder>`, `GAME_EXTRA` += `port/modules.cpp`, `-DCAFE_PORT_MODULES`, and put
`mk8-data-imports.map` next to the program as `data-imports.map`.

The system font is not part of a game dump either: copy your console's `CafeStd.ttf` to `build-NAME/fonts/`.

## License

The files here are under the MIT license, as the projects they build on. Third-party code keeps its own license.
