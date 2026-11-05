# Asset preservation and rights review ? v2.1

All runtime resources are under assets/. The 50 original media files retained
in v2.0 plus seven supplied power-up placeholders make **57 media files**.
Three historical script snapshots also remain, giving 60 migration records.
No icon was redesigned, no external recording was added and no source asset
was discarded. docs/previews/ contains runtime screenshots, not game assets.

ASSET_MIGRATION.json records original, previous_path (the location immediately
before this move), current path and SHA-256. Original hashes remain unchanged.
The supplied placeholder names retain their original filenames/extensions.
The duplicate historical font is preserved, not introduced by v2.1.

## Runtime and retained resources

- assets/px/branding/: original logo.png, title.png and Gtitle.png. The emblem
  is used on the redesigned screens; historical title images are still cached.
- assets/px/powerups/: power_up_magic_bean.png, power_up_sabotage.png,
  power_up_flaming_ball.png, power_up_ghost.png, power_up_laser.png,
  power_up_shield.png and power_up_lightning.png. The first six are gameplay
  placeholders; Lightning is retained/decoded but excluded from play.
- assets/px/fonts/: WRESTLEMANIA.ttf and legacy/WRESTLEMANIA-root.ttf are
  retained. The redesigned UI uses Pygame's bundled default font instead.
- assets/px/legacy/: all unused images/variants and the separate Games_files
  backgrounds/logos, grouped by their former directory.
- assets/snd/music/: the original eight music files, including unused
  old_generique.wav. Fun reuses the Classic track; no new track is added.
- assets/snd/sfx/: original effects. Pickup reuses plusOne.wav and Shield
  reuses reboundVsWall.wav. Unused recordings remain untouched.
- assets/snd/legacy/: the separate Games_files recordings and retired encodings.

All 57 media files decode with real Pygame decoders in the automated suite.
Successful decoding and retention do not establish permission to redistribute.

## Owner's visual provenance statements

The project owner states that:

- Predator branding and original game graphics were created by the project owner.
- Third-party visual resources were obtained under free-use licenses.

These statements record supplied provenance, not independently verified license
terms. They do not mean that every asset is public domain, remove attribution
obligations, or establish a single license covering all files. Existing license
information and attribution requirements must be preserved. No assets, license
records or historical source credits are changed by this refinement.

Specific license names, source links, per-file mapping and applicable attribution
requirements for third-party visuals have not yet been documented here. This
includes power-up placeholders and legacy resources whose source mapping is
uncertain. The names ultimatearm and Vectors_Market in filenames remain clues,
not complete credits. Record applicable terms individually without substituting
invented terms for the owner's statement of free use.

## Sound and font provenance: separate review

The statements above concern visuals; they do not establish the source or
permissions of music, effects or fonts. Review sound recordings, including
retired versions, individually and preserve their actual license/attribution
information when available.

WRESTLEMANIA.ttf and the legacy duplicate require their own provenance record.
Do not infer a license from the filename. The current UI uses Pygame's bundled
default font; retain the dependency's applicable notices. No new sound/font
licensing terms or source-code license are assigned here.

## Credits

The in-game credits identify the HEI School Project, Peter Clement LEROY's
current game design/redevelopment/programming, and Original Predator branding.
See [credits documentation](CREDITS.md). The archived school script's Clement
LEROY attribution remains unchanged. Technical development details and asset
review paths stay in documentation rather than the in-game panel.
