# Assets retained and provenance review

All **50 original asset files** are retained. No asset was deleted or replaced.
The complete old → new file mapping, including the three archived scripts,
is recorded with SHA-256 checksums in ASSET_MIGRATION.json. Tests verify those
files still match. No license or provenance information was found alongside
the files; retention and successful decoding do not establish redistribution
rights.

## Active resources

| Directory | Used by the game |
| --- | --- |
| sounds/music/ | generique.mp3, Menu.wav, 2joueurs.wav, PODER.wav, VsIA.wav, VsWall.wav, 4joueurs.wav |
| sounds/effects/ | reboundJoueur2.wav, reboundWallH.wav, reboundVsWall.wav, losing.wav, plusOne.wav, minusOne.wav, speed.wav, nani.wav |
| px/images/ | logo.png, title.png, Gtitle.png |
| px/fonts/ | WRESTLEMANIA.ttf |

These 19 unique files are declared centrally in src/assets.py. Music is
streamed; effects, images and fonts are cached. All active audio, image and
font files were loaded using real Pygame decoders during automated checks.

## Retained but unused

- sounds/music/old_generique.wav: alternate intro; not automatically substituted.
- sounds/effects/: bug.wav, fall.wav, reboundIA.wav, reboundJoueur.wav,
  win.mp3 and winA.mp3. No active use was found in the school script.
- px/images/: images.png, gold_tribute_ultimatearm.png,
  diamond_tribute_Vectors_Market.png, logo_N.jpg, logo_Bt.jpg, logo_B.jpg,
  logo_Nt.jpg and logo_RB.png. These may be alternate branding or planned
  rewards; their filenames alone do not establish a purpose or author.
- sounds/legacy/ and px/legacy/: the whole separate Games_files asset set,
  including retired audio encodings. No current source references them.
- px/fonts/legacy/WRESTLEMANIA-root.ttf: retained root font duplicate.

Unused files remain available for the owner to review. No decisions to discard
or activate them were inferred from their names.

## Manual review before public redistribution

Confirm the creator/source, permitted redistribution, required attribution
and any modification terms for **every music track, sound effect, font and
image**, including unused files. In particular:

- Establish the source and permissions of the named music and effect recordings.
- Check WRESTLEMANIA.ttf's font license rather than assuming its filename
  identifies rights or an author.
- Review school/HEI branding and all logo variants for ownership and permitted use.
- Investigate the apparent credit cues `ultimatearm` and `Vectors_Market` in
  image filenames; do not treat them as complete or verified attribution.
- Review Games_files backgrounds, logos and audio independently of the school set.
- Have the owner choose a source-code license. None is invented in this patch.

Original authorship credited by the script remains Clement LEROY. No additional
asset authorship, copyright ownership or public release permission is claimed.
