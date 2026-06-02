# Photographic Style Spatial Source Ablation - 2026-06-02

## Executive Summary

This pass adds a reproducible ablation workflow for Apple Photos Photographic Styles HEICs:

- Tool: `tools/style_spatial_ablation.py`
- Plan: `docs/plans/active/photographic-style-spatial-source-ablation-20260602.md`
- Run: `artifacts/style_spatial_ablation/20260602_v1_source_ablation/`
- Manifest: `artifacts/style_spatial_ablation/20260602_v1_source_ablation/manifest.json`
- Manual table: `artifacts/style_spatial_ablation/20260602_v1_source_ablation/README.md`

The run uses the previously user-confirmed Photos-activating baseline:

`artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic`

and a donor metadata source:

`Apple_Native_Samples/IMG_0033.HEIC`

The generated variants are structurally valid and decode with auxiliary images. They are not automatic proof of Apple Photos spatial-rendering behavior; the Photos import/edit observations remain manual evidence.

## Generated Experiments

The final run generated 10 HEIC files:

| Variant | Changed role family | Preserved key candidates |
|---|---|---|
| `baseline_original.heic` | none | all |
| `neutral_base_only.heic` | primary/base image | styledeltamap, linearthumbnail, HDR gain map, tmap, bplist, Exif/MakerNote |
| `neutral_styledeltamap_only.heic` | styledeltamap grid children | base, linearthumbnail, HDR gain map, tmap, bplist, Exif/MakerNote |
| `neutral_linearthumb_only.heic` | linearthumbnail | base, styledeltamap, HDR gain map, tmap, bplist, Exif/MakerNote |
| `neutral_base_styledelta_linearthumb.heic` | base, styledeltamap, linearthumbnail | HDR gain map, tmap, bplist, Exif/MakerNote, sky matte |
| `sky_matte_black.heic` | semantic sky matte | base, styledeltamap, linearthumbnail, HDR gain map, tmap, bplist, Exif/MakerNote |
| `sky_matte_white.heic` | semantic sky matte | base, styledeltamap, linearthumbnail, HDR gain map, tmap, bplist, Exif/MakerNote |
| `linearthumb_shift_x.heic` | linearthumbnail | base, styledeltamap, HDR gain map, tmap, bplist, Exif/MakerNote |
| `styledelta_shift_x.heic` | styledeltamap grid children | base, linearthumbnail, HDR gain map, tmap, bplist, Exif/MakerNote |
| `bplist_swapped_only.heic` | style metadata bplist | base, styledeltamap, linearthumbnail, HDR gain map, tmap, Exif/MakerNote |

Linearthumbnail ablations use VideoToolbox, not x265, to keep the Apple-like single-IDR payload and 105-byte `hvcC` profile from the prior activation-sensitive findings.

## Automatic Validation

For every generated HEIC:

- `heif-info`: exit success.
- `tools/heif_dump.py`: JSON and Markdown generated.
- `heif-convert --with-aux --no-colons`: primary plus aux PNGs decoded.
- `tools/styledeltamap_diagnostics.py`: aux stats generated.
- `tools/semantic_fitter.py`: JSON and Markdown generated with zero hard warnings.
- Manifest records changed role families, replaced item IDs/types, preservation flags, role hashes, role inventory, and manual Photos fields.

Key automatic decoded facts:

- `neutral_base_styledelta_linearthumb.heic` decodes primary as constant `[128,128,128]`.
- Its linearthumbnail decodes as constant `[129,129,129]` after VideoToolbox/libheif roundtrip.
- Its styledeltamap decodes as constant `[128,128,127]`.
- Its HDR gain map remains non-neutral: mean about `[167.599,167.599,167.599]`, std about `[12.584,12.584,12.584]`.
- `sky_matte_black.heic` sky matte decodes to all `[0,0,0]`.
- `sky_matte_white.heic` sky matte decodes to all `[255,255,255]`.
- `neutral_linearthumb_only.heic`, `linearthumb_shift_x.heic`, and the triple-neutral variant all keep linearthumbnail NAL types `[20]` and `hvcC` length 105.

## Proven

- The workflow can generate role-targeted ablations without changing source files in place.
- The final run produced the minimum required variants plus per-file dumps, semantic reports, aux diagnostics, decoded aux PNGs, manifest, and manual test table.
- Each output has a parseable HEIF graph and zero `semantic_fitter` hard warnings.
- The manifest distinguishes structure validation from manual Apple Photos validation.
- Sky matte black/white files are available for reproducing the friend's low-priority exclusion test.
- The bplist swap variant changes only the style metadata role hash while preserving base, styledeltamap, linearthumbnail, HDR gain map, tmap, and Exif/MakerNote payload families.

## Strong Evidence

- Prior user observation says `apple_style_injected_from_preview_heic_v1.heic` activates Photographic Styles in Apple Photos. This run uses that as the baseline, so the ablations start from a Photos-facing artifact rather than a parser-only artifact.
- Prior local evidence supports that linearthumbnail is activation-sensitive: generated x265/multi-NAL forms were riskier, while VideoToolbox single-IDR linearthumbnail with 105-byte `hvcC` is the safer profile. The new linearthumbnail ablations preserve that profile.

## Weak Evidence / Manual Pending

These require importing the generated HEICs into Apple Photos:

- Whether `neutral_base_only.heic` still activates Styles UI.
- Whether `neutral_styledeltamap_only.heic` changes tone/color spatial response.
- Whether `neutral_linearthumb_only.heic` changes tone/color spatial response.
- Whether `neutral_base_styledelta_linearthumb.heic` still shows original spatial light/dark residual.
- Whether the response follows `linearthumb_shift_x.heic` or `styledelta_shift_x.heic`.
- Whether black/white sky matte variants look the same in Photos.
- Whether `bplist_swapped_only.heic` changes response without breaking UI activation.

## Excluded Or Low Priority

Nothing is fully excluded by automatic evidence alone.

If manual Photos testing confirms `sky_matte_black.heic` and `sky_matte_white.heic` are visually equivalent to baseline for tone/color response, then semantic sky matte can be treated as low priority for this sample family. The current run only proves the black/white files were generated and decoded correctly.

## Still Unknown

If the triple-neutral variant still shows original spatial response in Photos, the remaining preserved candidates are:

- HDR gain map.
- `tmap` item payload and `dimg` relation.
- Style metadata bplist, including binary keys.
- Exif/MakerNote private payload.
- Preserved item graph order, `iref`, and `ipma` associations.
- Other payloads or metadata not yet classified by role.
- Photos-side cache or import heuristics.

The current run does not neutralize HDR gain map, `tmap`, or MakerNote. They are explicitly recorded as preserved candidates so a residual result can be interpreted correctly.

## Response To Friend's Claims

### "Linear thumbnail has influence but is not everything"

Supported as a working hypothesis by prior activation-sensitive linearthumbnail evidence, but not proven by this automatic run. The new `neutral_linearthumb_only.heic` and `linearthumb_shift_x.heic` are the correct manual Photos tests.

### "Base/styledeltamap/linearthumbnail all neutralized still leaves original spatial residual"

Not yet reproduced automatically. The run provides `neutral_base_styledelta_linearthumb.heic`, where those three decoded surfaces are flat. Import this file into Photos and record whether tone/color still shows original spatial structure.

### "Sky matte is not the key factor"

Not automatically proven. The run provides `sky_matte_black.heic` and `sky_matte_white.heic`, and both decode exactly as black/white. If Photos behavior matches baseline for both, that supports excluding sky matte for this sample family.

### Most likely residual sources if triple-neutral still has structure

The highest-value next candidates are HDR gain map and `tmap`, followed by style bplist binary keys and Exif/MakerNote. This ordering is based on the triple-neutral variant preserving HDR/tmap/bplist/Exif while removing base/styledeltamap/linearthumbnail spatial content.

## Next Experiments

1. Manually test all 10 current variants in Apple Photos and fill the run README table.
2. Add `gainmap_neutral.heic` with HDR gain map neutralized while preserving base/tmap links.
3. Add `tmap_swapped_only.heic` and `tmap_neutral_payload.heic`, with the warning that invalid `tmap` payloads may break import.
4. Add `makernote_swapped_only.heic` using a donor Exif/MakerNote payload, separate from bplist swap.
5. Add donor/recipient cross-swaps for HDR gain map plus tmap together.
6. Repeat the triple-neutral test on a second Photos-activating baseline to reduce sample-specific overfitting.

## Verification Log

Commands run during implementation:

```bash
python3 -m unittest tests.test_style_spatial_ablation -v
python3 tools/style_spatial_ablation.py --baseline artifacts/constructed/apple_style_injected_from_preview_heic_v1/apple_style_injected_from_preview_heic_v1.heic --donor Apple_Native_Samples/IMG_0033.HEIC --output-root artifacts/style_spatial_ablation --run-id 20260602_v1_source_ablation --linearthumb-encoder videotoolbox
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m pytest tests/ -v
python3 -m compileall tools tests
git diff --check
```

Results:

- Focused ablation unittest: 7 tests OK.
- Real ablation generation: completed, manifest written, 10 variants generated.
- Manifest validation: all variants have successful `heif-info`, `heif_dump`, aux diagnostics, and semantic fitter reports; all semantic hard warning counts are 0.
- Full unittest discovery: 108 tests OK, 3 skipped.
- Plain pytest: unavailable in the active `python3` environment (`No module named pytest`).
- `compileall`: OK.
- `git diff --check`: OK.
