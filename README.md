# Mario Kart 8 (Wii U): native build, work in progress

An attempt to run the Wii U game as a native Linux (and Windows) program by static recompilation: the game's
PowerPC code is translated to C++ ahead of time and runs on a reimplementation of the Wii U's system libraries.
No emulator.

> **No game files are included.** You need your own dump of the game (Europe), unpacked to `code/`, `content/`,
> `meta/`. The translated C++ and the program built from it contain the game's code: do not share them.
> Not affiliated with or endorsed by Nintendo.

## Selbst bauen / Build it yourself

One command builds the native program from **your own dump** of Mario Kart 8. Nothing from the game is in this repository
or downloaded by the scripts: the game's code (Turbo.rpx, mvplayer.rpl) is translated to C++ and compiled on your computer.
*Ein Befehl baut das native Programm aus deinem eigenen Dump; nichts vom Spiel ist hier enthalten oder wird geladen.*

**You need / Du brauchst**
- your own dump of the game, **unpacked**: a folder with `code/`, `content/`, `meta/` (as Cemu or a Wii U dumper
  such as Dumpling gives it; `.wua`/`.wud` images must be unpacked first). Tested with Europe
  (000500001010ED00); other versions are translated from your files the same way and may work.
- Windows 10/11 64-bit or Linux x86-64; a CPU with AVX2/FMA (Intel Haswell, AMD Zen or newer); a GPU with a Vulkan driver.
- internet for the build tools and the pinned sources (Smash4PC `f145e7f`, ZArchive, addrlib, Vulkan-Headers from GitHub).
- about **2 GB** free in this folder (plus about 3 GB for MSYS2 on Windows) and 8 GB of RAM or more.
- time: about **5-15 minutes** for the first build on an 8-core PC; a second run only redoes what changed.

**Miis / Mii-Dateien.** Visible Miis need the Mii resource title (`0005001B-10056000`, files `FFLRes*.dat`) from **your own Wii U** — it is not part of the game, not in this repository and never downloaded. This game does not get far without it. Give the setup a Cemu-style `mlc01/sys` folder that holds `title/0005001b/10056000/content/` (`-SysDir` on Windows, `--sys` on Linux); it is written into the starter as `CAFE_SYS_DIR` and only read.
*Deutsch:* Sichtbare Miis brauchen den Mii-Systemtitel deiner **eigenen** Wii U (z. B. aus Cemus `mlc01/sys`), angegeben mit `-SysDir` bzw. `--sys`. Er ist nicht im Spiel-Dump und nicht hier enthalten.

**Windows** (PowerShell):

```powershell
git clone https://github.com/SirWinstonChurchillTheFirst/mario-kart-8-native
cd mario-kart-8-native
powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1 -GameDir "D:\Games\Mario Kart 8" -SysDir "D:\Cemu\mlc01\sys"
.\play\Start.bat
```

It installs [MSYS2](https://www.msys2.org) with winget if it is missing and the build packages into its CLANG64
environment with pacman (clang, lld, cmake, ninja, Python, git, SDL3, Vulkan loader + headers, shaderc, zlib, zstd,
xz, DejaVu fonts). Without `-GameDir` it asks for the folder. `-Jobs N` limits the parallel compile jobs; the build
runs at low priority so the PC stays usable.

**Linux** (Debian/Ubuntu, Arch, Fedora; others: install the same packages yourself):

```bash
git clone https://github.com/SirWinstonChurchillTheFirst/mario-kart-8-native
cd mario-kart-8-native
./setup-linux.sh "/path/to/Mario Kart 8" --sys ~/.local/share/Cemu/mlc01/sys
./play/start.sh
```

Missing packages are installed with sudo (apt: clang cmake ninja-build git python3 pkg-config zlib1g-dev libzstd-dev
libssl-dev libvulkan-dev libshaderc-dev fonts-dejavu-core, and libsdl3-dev where the distribution has it; without it
SDL 3.2.26 is built from source, e.g. on Ubuntu 24.04). `--jobs N` limits the compile jobs.

**What the setup does** (`tools/native-build.sh`, the same on both systems): checks your dump; clones
[Smash4PC](https://github.com/josiahg2502-glitch/Smash4PC) at `f145e7f` and the three pinned dependencies; applies
`port/upstream-local.patch` (all runtime/recompiler changes, made by the `port/patch_*.py` scripts in order); builds the
recompiler `cafe-recomp`; translates your `code/`; compiles runtime + translated game; and puts `cafegame`, a stand-in
font and the starter into `play/`. Everything it makes stays in `build/` and `play/` (both ignored by git): they hold
code translated from the game — **keep them for yourself, do not share them.**

The Wii U system font is not part of a game dump: DejaVu Sans stands in (`play/fonts/CafeStd.ttf`); put your console's
own `CafeStd.ttf` there to replace it. Saves go to `play/save/`. The system language follows your PC
(`CAFE_LANGUAGE=de|en|fr|...` overrides it).

**Getestet / tested (23 Nov 2026):** `setup-windows.ps1` in an empty folder on Windows 11 (i7-13700KF, RTX 3070 Ti, 8 jobs, `-SysDir` with the tester's own Mii files): video module translated and loaded, the whole build took about 3 minutes; `Start.bat`'s program went from the title through the menus into a race at Mario Kart Stadium (57-58 frames/s with picture captures on). The translation is the same as the console build's (only the newer recompiler's `dcbf` lines differ). The same scripts were run end to end from an empty folder on 23 November 2026: Lost Levels and Mario Kart 8 on Windows 11, Lost Levels on Ubuntu 26.04 and on a fresh Ubuntu 24.04 (SDL3 built from source there), Mario Party 10 on Windows 11.

## Status (24 November 2026): races run at 59-60 frames/s on a Batocera console with the graphics fixes, menu videos play

| Step | State |
| --- | --- |
| Title, menus, cup/character/kart select | works (PC and console) |
| A race (Mario Kart Stadium) with the other racers | works: lit track, karts, drivers, HUD, sound |
| Speed | console (Ryzen 3 4350GE, Vega 6), Grand Prix at Mario Kart Stadium: 59.6 frames/s on average in the race, slowest 10 s 58.4-58.8, longest frame 40-48 ms (no hitch over 100 ms), menus 59.9, track loading frame 300 ms (was 710-780); CPU 71-75 C, GPU 65-66 C |
| Menu preview videos | work where FFmpeg's `libavcodec` (.so.61 or .58) is installed: the runtime's H.264 decoder interface (`port/os_extra.cpp`, `patch_h264.py`) hands the stream to it at run time; without it the frames stay black (sound plays) |
| Online, Mario Kart TV upload | not available |

**Miis.** The game asks for the Wii U's Mii resources (system title `0005001B-10056000`). They are **not** part of
the game and **not** included here: point `CAFE_SYS_DIR` at a Cemu-style `mlc01/sys` folder holding
`title/0005001b/10056000/content/` from your own Wii U.

## 24 November 2026: graphics fixes and speed

- **Picture.** Light flicker and bleached karts, kart shadows (compare sampling in the shader), missing letters in menu
  text, cube-map arrays for reflections, depth and compressed texture slices, menu videos that stood still, a
  music-stream crash (`patch_seq_ps.py`, `patch_shadow_compare.py`, `patch_cube_arrays.py`, `patch_depth_slices.py`,
  `patch_compressed_slices.py`, `patch_slice_clear.py`, `patch_texture_stores.py`, `patch_out_of_memory.py`, ...).
- **Speed (measured on the console, all fixes are general runtime changes, not for this game only):**
  - slice-target lookups are cached per texture and the texture layout is computed once (`patch_slice_cache.py`,
    `patch_texture_surface_cache.py`): a texture bind costs 0.6-0.8 us instead of 1.5-1.7;
  - the frame is handed to the GPU in parts every 2 ms instead of all at the end, so the GPU works while the frame is
    still being recorded (`patch_submit_chunks.py`, `TTT2_SUBMIT_MS`, 0 = old way); this gave the most;
  - textures not used for 10 s were freed and made again at once (hitches of 110-190 ms); now they stay while all
    textures together are under `TTT2_TEXTURE_BUDGET_MB` (768) (`patch_texture_retention.py`), and small images come
    from 64 MB memory blocks (`patch_image_pool.py`, `TTT2_IMAGE_POOL=0` = old way): track loading 300 ms instead of 750;
  - `TTT2_GUEST_DMABUF=1` (set in the console's start script) makes each GPU submission cheaper.
- Open: render targets are never freed (4250 -> 5020 in a 250 s race); very long sessions are not measured yet.

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

By hand (what `tools/native-build.sh` does for this game): translate `mvplayer.rpl` with `CAFE_RPL_REBASE=06000000,00300000 CAFE_DATA_IMPORT_FIRST=32`,
rename its tables with `module_rename.py`, write the map with
`tools/make_data_imports.py <game>/code/mvplayer.rpl 00300000 mk8-data-imports.map`, translate `Turbo.rpx` with
`CAFE_DATA_IMPORT_MAP=mk8-data-imports.map`,
configure with `-DGAME_MODULE_DIRS=<module folder>`, `GAME_EXTRA` += `port/modules.cpp`, `-DCAFE_PORT_MODULES`, and put
`mk8-data-imports.map` next to the program as `data-imports.map`.

## License

The files here are under the MIT license, as the projects they build on. Third-party code keeps its own license.
