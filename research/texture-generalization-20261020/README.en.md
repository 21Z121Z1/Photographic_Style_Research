# Texture generation from real XDRemux fixtures

This extends the image-derived Apple SPI producer to multiple native person instances, empty person contexts, non-square rasters, source orientation and different input resolutions. It generates a new SDR editing copy. The source fixture bytes, HDR resources and embedded motion video are not rewritten; HDR and motion are not carried into this copy.

The earlier NASA candidate, SHA-256 `a7ac5d0dc8721e0cac4db6bfec153864f96fc83f406adeedc2036bc6f0543a7b`, has [user-confirmed device activation](https://github.com/21Z121Z1/Photographic_Style_Research/blob/38f1216a567cc57c993b5e5646f6b0a0d944a18e/DEVICE_ACTIVATION.json). New candidates require their own device test. Native production/readback/replay receipts and device reports are separate evidence.

## Convert an image

Use Apple-silicon macOS 27 and Xcode 27. The command compiles the original-framework caller tools, applies the source's orientation once, converts into an explicit sRGB/8-bit SDR working image, infers this image's resources, and generates a HEIC with native verification:

```sh
python3 research/texture-generalization-20261020/convert.py \
  /path/to/photo.heic /tmp/texture-photo --max-dimension 1024
```

The output directory must be empty. Import `texture-candidate.heic`; `control.heic` has the same encoded primary pixels without the new editing resources. Each `person-N/final-file-mattify-preview.heic` is an independently rendered, baked single-person effect preview. It is not the editable candidate or a combined multi-effect preview.

The default long edge is 1024 pixels. The CLI also accepts 512, 1536, 2048 and 4096; measured coverage is reported in the matrix, rather than implied by an accepted argument. Original-resolution HDR conversion and Live Photo preservation are outside this editing-copy contract.

## Inference and production

ImageIO supplies one upright raster to the entire pipeline. Native Vision produces face landmarks, segmentation and separate person probability masks. Masks are explicitly resampled to the working dimensions before both statistics production and encoding. Face/instance assignments use probability overlap in the measured face bounds, with distinct instance bindings. Unmatched faces are reported; an aggregate person mask never substitutes for a keyed instance mask.

For each matched face, the original Mattify, UnderEyeBrighten and SkinSmoothStandalone entries run with shared geometry and the appropriate instance mask. They receive no supplied capture statistics. Small-face inputs can return an empty effect-statistics dictionary despite successful native operations. Such a group is omitted and reported, rather than filled with defaults or another image's data. Empty person contexts contain no invented person, landmarks or skin/person population statistics. Native segmentation false positives remain model results, not a verified classification of every depicted object.

The working output image is initialized before native statistics, and command completion is checked. The writer gives each person a unique XMP `InstanceMaskReferenceKey`. Native readback must preserve that binding, geometry and every available statistics group. Final-file replay decodes the actual encoded masks and uses the final image and stored per-person statistics; it performs no fresh Vision inference. An empty context has no person effect to replay and is recorded accordingly.

The ordinary Styles prerequisite is a newly measured SDR identity-edit context. Negative native linear components are recorded, then clamped for this nonnegative SDR context. No original camera RAW, ISP or capture settings are inferred. The native tuning target selects an editing profile. Landmark-derived nose/lip/eyebrow regions, inferred skin intersected with face bounds, hand-pose regions and disabled optional ear/tattoo protection retain the resource-origin distinctions in the [producer report](../texture-producer-20261020/README.md).

## Fixture matrix and acceptance

The manual research workflow pins XDRemux at `18340989590d451f5676924feb03c70baa503e1a` and verifies all 28 media entries against `fixtures/SHA256SUMS`. Two entries are duplicate bytes, leaving 26 independent originals. The matrix processes each unique source once and keeps the duplicate mapping.

```sh
python3 research/texture-generalization-20261020/matrix.py \
  /path/to/XDRemux/fixtures /tmp/texture-fixtures --phase generate --selection all
```

Supplemental cases use those real sources: a crop/composite of two detected faces, inverse raster transforms paired with EXIF orientations 2 through 8, and 512/2048 resolution variants. The composite must read back two independently bound people. Orientation tests require byte-identical upright native pixels before production. The prior NASA input is a separate regression case. A direct CLI invocation is also tested. These derived cases are identified separately from original photos.

Each `acceptance.json` checks native operation results, input/mask hashes, shared geometry, stored statistics and instance keys, primary-payload preservation, native final-mask decoding and finite per-person replay output. Nonzero changes are reported; an inapplicable effect can legitimately produce zero changes. `matrix.json` records every failure and omitted group, the source commit and fixture commit. It is the authority for the executed coverage and pass counts.

New native outputs are preserved on `research/texture-matrix-output-<run-id>` without merging or changing the source branch. Each case archive contains a file manifest with byte lengths and SHA-256 digests. Native programs receive no repository credential; only the final preservation step receives its scoped workflow token. No Apple implementation or system model is patched, and Photos is not opened by the workflow.
