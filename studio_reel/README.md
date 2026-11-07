# Mirabilis On — current delivery

Use `media/studio/mirabilis-ai-javobi.mp4`, `mirabilis-ai-cover.jpg`,
`mirabilis-ai-production.json` and `mirabilis-caption.txt` for the current
publication. Masthead: MIRABILIS ON; physical chip engraving: MIRABILIS;
account footer: @mirabilis_on. The two chip shots were rendered again with the
updated lettering, including its animated layer attachment. Shots 3–4 reused
the original clean geometry frames. All four final shots were inspected and
decoded audio hashes match the original. See the publication index for schedule.
The earlier MP4s below are historical exports, not the current publishable file.

# Javob ortida — original 3D Instagram film

An 18-second original Uzbek AI-literacy Reel for Safeguard On. Four physically
rendered scenes: a titanium AI package, its separated layers/token tiles, a
network of moving signals, and an answer/uncertainty end shot. All geometry,
materials, lighting, camera choreography, typography and music are original.
No stock footage, model-generation API calls, real product UI or voice clones.

The visuals are explicitly labeled as a simplified conceptual depiction, not
an actual model architecture or product demonstration. Caption sources explain
tokens and next-token prediction; the video does not claim all AI is only a
language model. Music and transition effects are synthesized locally; no spoken
narration is included.

## Reproduce

Requirements: Blender 4.3+, Python with Pillow/NumPy, FFmpeg with minterpolate,
Open Sans fonts, optional official Open Image Denoise 2.x CPU runtime.

```sh
blender -b -t 3 --python studio_reel/scene.py -- --out .local/studio/frames --samples 8 --size 432 --fps 12
python studio_reel/finish.py --root .local/studio --oidn-lib /path/to/libOpenImageDenoise.so --denoise-only
python studio_reel/finish.py --root .local/studio --output .local/studio/safeguard-javob-ortida.mp4
```

The chosen CPU profile renders 432×768 at 12 fps. OIDN cleans the rendered
frames, optical flow brings each shot separately to 24 fps, and the final edit
adds native 1080×1920 typography. This is not native 1080p path tracing. For
more detail, increase render resolution and samples, at the cost of CPU time.
The supplied finisher expects 54 frames per 4.5-second shot at this profile.

OIDN is a local denoiser, not a generative video service. For this run the
official RenderKit v2.5.1 Linux archive was downloaded and its published SHA256
verified: `743c3e2aff8c220d5d70fe6cb970fb3d36f2702d2693c61d1d148e404cf37cd6`.
Download binaries only from the official [OIDN releases](https://github.com/RenderKit/oidn/releases).
Do not commit binaries or intermediate frames to the source repository.

`--preview` renders only a middle frame of each scene. `finish.py --watch
--denoise-only` can clean completed frames while rendering continues. Existing
frame files are preserved; use a new output directory if changing render
settings. This studio film is a separate creative artifact and does not replace
scheduled Instagram posts or change VPS services.

## Delivered artifact

`media/studio/` contains the final 18-second MP4, a cover, Uzbek caption,
on-screen-text SRT and machine-readable production report. The export has 432
frames at 24 fps and stereo 48 kHz AAC. Four representative frames and the
uncertainty title were visually inspected; technical audio checks measured
-17.6 dB mean and -1.3 dB maximum level. No subjective audio audition is claimed.
The film has not been posted or scheduled on Instagram.

Verification command:

```sh
python studio_reel/verify.py media/studio/safeguard-javob-ortida.mp4
```

## Account handle update — 2026-11-07

The current Instagram handle is `@mirabilis_on`. The finisher now uses this
footer. The existing delivered MP4 still contains `@safeguard_on`; preserve it
as the historical creative reference and re-export before any new publication.
The user changed the username only; the visible brand name has not been changed.

## Current delivery — username refresh

`media/studio/mirabilis-javob-ortida.mp4` is the new 18-second export with
`@mirabilis_on` in all four shot footers. Its cover is `mirabilis-cover.jpg`
and verification report is `mirabilis-production.json` in the same directory.
Decoded PCM audio SHA256 matches the original film exactly. Four final frames
and their footer crops were visually inspected. This revision is not scheduled.
The original MP4 remains unchanged as a historical reference.
