# Style Semantic Payload Fitting Plan

Date: 2026-05-28

## Goal

Advance from a structurally Apple-like styledeltamap HEIC toward a scene-fitted Apple-private payload family, without losing the Photos style-control behavior already observed for `apple_parity_styledeltamap_v3c.heic`.

The immediate target artifact is a new candidate built from the IMG_0342 pair that keeps the v3c working graph, fixes the v4 transform encoding bug, and replaces only the auxiliary payloads whose generated form can be validated against Apple sample invariants.

## Evidence From Current Workspace

Known-good user result:

- `artifacts/constructed/apple_parity_styledeltamap_v3c/apple_parity_styledeltamap_v3c.heic`
- User reports style-related controls work.
- Primary is displayed as `3024x4032` with `irot=270`.
- Styledeltamap and HDR gain map are generated from the preview, while linearthumbnail and Exif/MakerNote remain template-copied.
- Style metadata item `101` is already scene-touched: only `6.LinearImage` differs from the Apple template.

Failing current result:

- `artifacts/constructed/apple_parity_styledeltamap_v4/apple_parity_styledeltamap_v4.heic`
- User reports custom linear thumbnail, styledeltamap, and HDR gain map exist, but style controls no longer work.

Concrete differences found:

- `item101` style bplist is byte-identical between v3c and v4, so item 101 alone is not the v4 regression.
- `item102` Exif differs: v4 mixes preview standard Exif fields with the template MakerNote. This keeps Apple MakerNote tags `0x0054` and `0x005a`, but leaves the MakerNote from the template scene.
- `item97` linearthumbnail differs: v3c copies the Apple template payload; v4 uses a generated payload. v4 decoded output uses almost the full 8-bit range, while the Apple/v3c linearthumbnail is a narrower range centered near 128.
- v4 has an invalid `irot` item property. Apple template and v3c property index 4 are one payload byte (`03`). v4 writes a FullBox-like 5-byte payload (`0000000000`). `heif_dump` tolerated it, but `exiftool` reports `Rotation: Unknown (0 0 0 0 0)`.

The invalid `irot` is a standards bug and must be fixed first because all non-tmap image and aux items share property index 4. It is independent of private Apple semantics.

## External Constraints Used

- HEIF auxiliary data must be discoverable through item references and item properties, not merely as extra images.
- Image rotation item property (`irot`) is a compact item property, not a FullBox. The local Apple samples confirm a one-byte payload.
- Apple ImageIO exposes HEIF auxiliary data as an auxiliary data dictionary plus data description; this supports treating the private style family as a linked graph of image payloads and metadata, not only `auxC`.
- ISO 21496-1 / `tmap` remains separate from styledeltamap. Do not invent or patch `tmap` metadata unless a real gain-map metadata path is present.

## Implementation Steps

1. Add tests that fail on v4's bad transform encoding.
   - Assert generated landscape mode writes `irot` payload size 1.
   - Extend the dumper so invalid `irot` payload sizes are visible in JSON/Markdown.

2. Fix the writer.
   - Replace `_full_box("irot", ...)` with a normal `irot` box payload of exactly one byte.
   - Preserve tmap `ispe` landscape switching, because that property is a FullBox and its existing writer path is correct.

3. Tighten linear thumbnail generation.
   - Treat generated linearthumbnail as an affine-fitted Apple-like thumbnail source, not a raw preview resize.
   - Encode linearthumbnail with HEVC Main10 level 3.1 to match the Apple template linearthumbnail class.
   - Keep linearthumbnail generation opt-in until Photos confirms it does not break style controls.

4. Add a semantic payload report.
   - Compare a candidate against a working reference and a template.
   - Report hashes, sizes, item properties, decoded aux stats, `irot` payload validity, style bplist equality/differences, and Exif/MakerNote differences.
   - Use it to document the exact v3c-v4 regression and the new candidate.

5. Generate a new candidate.
   - Build an `apple_parity_styledeltamap_v5` artifact with:
     - primary grid from IMG_0342 preview,
     - generated styledeltamap tiles,
     - generated HDR gain-map tiles from MPF MPImage2,
     - fixed one-byte landscape `irot`,
     - scene-updated style metadata item 101,
     - preview/Apple MakerNote policy recorded explicitly,
     - generated linearthumbnail only if its validator passes; otherwise preserve the v3c/template linearthumbnail as the style-safe baseline.

6. Validate locally.
   - Unit tests pass.
   - `heif_dump` reports valid `auxC`, `auxl`, `dimg`, `tmap`, and one-byte `irot`.
   - `heif-info` reads the file as HEIC.
   - `heif-convert --with-aux --no-colons` extracts primary and aux images.
   - Semantic report shows no new hard error relative to v3c.

## Confidence Gate

Before claiming the goal is complete, ask:

- Is every ISO/HEIF structural bug found in v4 fixed by tests?
- Does the new artifact preserve every v3c property that correlates with the user-reported working style UI, unless the replacement is explicitly validated?
- Are all generated Apple-private payloads documented as experimental?
- Has Photos/ImageIO behavior been verified by import, not inferred from parser success?

If Photos/ImageIO UI behavior has not been re-tested, do not mark the goal complete. Produce the candidate and the evidence, then leave Apple Photos activation as pending external validation.
