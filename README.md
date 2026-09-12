# signde repository

Repository of skins for avdvplus/p3i based CoreELEC builds formerly maintained by jamal2362. 

See the [Kodi forum thread](https://forum.kodi.tv/showthread.php?tid=388348) for more information and discussion.

## Installation

1. Enable "Unknown Sources" in Kodi Settings > System > Add-ons
2. Enable "Update official add-ons from: Any repositories" in Kodi Settings > System > Add-ons
3. Install repository using zip or file manager source
    - Kodi File Manager Source: https://signde.github.io/repository.signde/
        - File Manager > Add Source > Edit/Add
            - Protocol: Web server directory (HTTPS)
            - Server address: signde.github.io
            - Remote path: repository.signde
    - ZIP Install: https://signde.github.io/repository.signde/repository.signde-1.2.zip
4. Install the skin from repo: signde repository > Look and Feel > Skins

## Changes

- September 12th 2026
    - signde PPI v15.2.7.5
        - Added a Top/Bottom option for the Dolby Vision pill in codec badges, with Top as the default (requested by @Aemstel via kodi forum).
        - Updated PPI to indicate when audio output is being decoded (requested by @MrMojoRisin85 via avsforum).

- September 9th 2026
    - Arctic Fuse 3 v70.3.2.19
        - Changed the Video OSD PPI/VS10 selector to open on Select/click or Up instead of automatically on focus
    - Arctic Fuse 2 v107.2.12.12
        - Changed the Video OSD PPI/VS10 selector to open on Select/click or Up instead of automatically on focus

- September 6th 2026
    - Arctic Fuse 3 v69.3.2.19: Updated to upstream v3.2.19
    - InfoTagger v0.0.9: Added required dependency for TMDb Helper v6.17.1
    - Texture Maker v0.2.11: Updated to upstream v0.2.11
    - signde PPI v14.2.7.5
        - Fixed VS10 dialog navigation so Player Process Info remains selectable
    - Arctic Fuse 2 v106.2.12.12
        - Fixed the Video OSD Player Process Info button
    - TMDb Helper v6.17.1: Updated to upstream v6.17.1
    - signde PPI v13.2.7.5
        - Forked TinyPPI as signde PPI under the independent `script.signde.tinyppi` add-on ID so it can coexist with the original add-on
        - Added the shared Player Process Info layout and CoreELEC 21 `Player.Process` integration
        - Added Classic and Modern background modes, with Classic as the default
    - Arctic Fuse 3 v68.3.2.16
        - Added Profile 7 MEL/FEL media flags
        - Delegated Player Process Info and playback codec badges to signde PPI
    - Arctic Fuse 2 v105.2.12.12
        - Restored the Interface setting used to enable custom media icons
        - Added an entirely new set of optional custom media icons, including Profile 7 MEL/FEL media flags
        - Delegated Player Process Info and playback codec badges to signde PPI
    - Aeon Nox Silvo v69.10.0.4
        - Assigned the independent `skin.aeon.nox.silvo.signde` add-on ID to prevent conflicts with upstream releases
        - Added Profile 7 MEL/FEL media flags
        - Fixed background video display
        - Delegated Player Process Info and playback codec badges to signde PPI
    - Arctic Horizon 2 v64.0.8.30
        - Added Profile 7 MEL/FEL media flags
        - Delegated Player Process Info and playback codec badges to signde PPI
    - Arctic Zephyr Reloaded v65.3.0.3
        - Added Profile 7 MEL/FEL media flags
        - Delegated Player Process Info and playback codec badges to signde PPI
    - Arctic Zephyr Martian v11.3.19.13
        - Assigned the independent `skin.arctic.zephyr.martian.signde` add-on ID to prevent conflicts with upstream releases
        - Added Profile 7 MEL/FEL media flags
        - Delegated Player Process Info and playback codec badges to signde PPI
    - Arctic Zephyr 2 Resurrection v68.1.0.52
        - Added Profile 7 MEL/FEL media flags
        - Delegated Player Process Info and playback codec badges to signde PPI
    - Bingie v39.2.0.2
        - Added Profile 7 MEL/FEL media flags
        - Delegated Player Process Info and playback codec badges to signde PPI
    - Confluence v66.5.1.3
        - Assigned the independent `skin.confluence.signde` add-on ID to prevent conflicts with upstream releases
        - Added Profile 7 MEL/FEL media flags
        - Delegated Player Process Info and playback codec badges to signde PPI
- August 31st 2026
    - TMDb Helper v6.16.7: Updated to upstream v6.16.7
- August 28th 2026
    - Studio Icons - Coloured v1.0.0027: Updated to upstream v1.0.0027
    - TMDb Helper v6.16.5: Updated to upstream v6.16.5
- August 21st 2026
    - Arctic Fuse 2 v101.2.12.12: Added optional audio channel-layout artwork, Dolby Vision enhancement-layer indicators, and unified modern Player Process Info styling
    - Arctic Fuse 3 v65.3.2.16: Added an option to hide audio channel-layout artwork and improved media flag compatibility with legacy and NFO codec values
    - Aeon Nox Silvo v65.10.0.4: Added an option to hide audio channel-layout artwork
    - Arctic Zephyr 2 Resurrection v66.1.0.52: Updated to upstream 1.0.52
    - TMDb Helper v6.16.4: Updated to upstream v6.16.4
    - Arctic Fuse 3 v64.3.2.16: Updated to upstream 3.2.16
    - Arctic Fuse 2 v100.2.12.12: Improved Atmos and DTS:X detection in library information and fixed stale codec information while browsing the library
    - Confluence v63.5.1.3: Improved Atmos and DTS:X detection in library and playback information
    - Arctic Horizon 2 v62.0.8.30: Improved Atmos and DTS:X media flag detection
    - Arctic Zephyr 2 Resurrection v66.1.0.51: Improved DTS:X media flag and label detection
    - Aeon Nox Silvo v64.10.0.4: Improved Atmos and DTS:X detection in library views and OSD information
- August 17th 2026
    - Aeon Nox Silvo v63.10.0.4: Added audio channel-layout artwork and Dolby Vision enhancement-layer indicators from Tiny PPI
- August 15th 2026
    - Arctic Horizon 2 v61.0.8.30: Added avdvplus/p3i support and improved Dolby Vision dual-track and L5 active-area information in Player Process Info
- August 14th 2026
    - Arctic Fuse 3 v64.3.2.15: Added audio channel-layout artwork and Dolby Vision enhancement-layer indicators from Tiny PPI
- August 7th 2026
    - Bingie v37.2.0.2: Added back missing VS10 and PPI assets
- August 2nd 2026
    - Arctic Fuse 3 v63.3.2.15: Updated to upstream 3.2.15
    - TMDb Helper v6.16.3: Updated to upstream v6.16.3
    - Arctic Fuse 3 v63.3.2.14: Updated media flag icons
    - Studio Icons - Coloured v1.0.0026: Updated to upstream v1.0.0026
- July 21st 2026
    - Arctic Fuse 3 v62.3.2.14: Updated to upstream 3.2.14, improved recovery after updating the active skin, and updated media flag icons
    - Arctic Fuse 2 v99.2.12.12: Fixed Dolby Vision L5 active-area offsets in Player Process Info
    - Aeon Nox Silvo v62.10.0.4: Fixed Dolby Vision L5 active-area offsets in Player Process Info
    - Arctic Zephyr 2 Resurrection v65.1.0.51: Fixed Dolby Vision L5 active-area offsets in Player Process Info
    - Arctic Zephyr Reloaded v63.3.0.3: Fixed Dolby Vision L5 active-area offsets in Player Process Info
    - Bingie v36.2.0.2: Fixed Dolby Vision L5 active-area offsets in Player Process Info
    - Confluence v62.5.1.3: Fixed Dolby Vision L5 active-area offsets in Player Process Info
    - TMDb Bingie Helper v2.1.0.3: Updated to upstream v1.0.3
    - Bingie Common v1.0.1: Updated to upstream v1.0.1
- July 18th 2026
    - Arctic Fuse 3 v61.3.2.13: Fixed L5 active offsets in PPI and hid footer media flags in wall views
- July 17th 2026
    - Arctic Fuse 3 v60.3.2.13: Added optional codec media flags in library footer, updated media flag icons, and improved media flag matching
    - TMDb Bingie Helper v1.0.4: Fixed Trakt in-progress widgets when episode counts are missing
- July 9th 2026
    - Arctic Fuse 3 v59.3.2.13: Updated to upstream 3.2.13
- July 7th 2026
    - Arctic Zephyr 2 Resurrection v64.1.0.51: Added source-quality media flags and improved Atmos media matching
- July 5th 2026
    - Bingie v35.2.0.2: Fixes for Trakt compatibility
    - Arctic Fuse 2 v98.2.12.12: Fixes for Trakt compatibility
    - Arctic Fuse 3 v58.3.2.11: Fixes for Trakt compatibility
    - Arctic Zephyr 2 Resurrection v63.1.0.51: Fixes for Trakt compatibility
    - Arctic Zephyr Reloaded v62.3.0.3: Fixes for Trakt compatibility
- July 3rd 2026
    - Arctic Zephyr 2 Resurrection v62.1.0.51: Fixed Atmos media badges in library views
    - Arctic Zephyr 2 Resurrection v61.1.0.51: Fixed small PPI display issues
    - Restored Arctic Zephyr 2 Resurrection v60.1.0.51
- June 27th 2026
    - Aeon Nox Silvo v61.10.0.4: Fixed small PPI display issues
    - Restored Aeon Nox Silvo v60.10.0.4
    - Bingie v34.2.0.2: Added missing heading icons on PPI
    - Bingie v34.2.0.2: Tweaked DTS-X and Atmos media icon matching - [11](https://github.com/signde/repository.signde/issues/11)
- June 24th 2026
    - Added Bingie support v33.2.0.2
    - Fixed small PPI display issues in Arctic Fuse 3 v57.3.2.11, Arctic Fuse 2 v97.2.12.12, Arctic Zephyr Reloaded v61.3.0.3, and Confluence v61.5.1.3
- June 21st 2026
    - Updated Arctic Fuse 3
    - Updated Skin Variables dependency
    - Restored Confluence
    - Restored Arctic Zephyr Reloaded
    - Restored Arctic Fuse 2
- June 20th 2026
    - Fixed repo branch paths
    - Restored Arctic Fuse 3
    - Initial repo creation
