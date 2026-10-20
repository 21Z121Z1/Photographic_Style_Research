# Image-derived Texture SPI production

For the configurable converter and real XDRemux fixture matrix, see [Texture generalization](../texture-generalization-20261020/README.en.md). The evidence below describes the earlier single-portrait production milestone; newer per-input results have separate receipts.

This research produces new Texture person statistics from a public input image, writes them with image-derived resources into a HEIC, and checks native readback and final-file effect replay. It is separate from the earlier preservation-only work.

**2026-10-20: the user confirmed that the delivered `texture-candidate.heic` activates on their device.** The candidate SHA-256 is `a7ac5d0dc8721e0cac4db6bfec153864f96fc83f406adeedc2036bc6f0543a7b`. The exact statement, delivered-artifact binding and unreported checks are archived in [DEVICE_ACTIVATION.json](https://github.com/21Z121Z1/Photographic_Style_Research/blob/38f1216a567cc57c993b5e5646f6b0a0d944a18e/DEVICE_ACTIVATION.json). Device model, OS version and a device-local checksum were not supplied. This is user-reported device evidence for this candidate, alongside the independently verified native generation and file evidence.

The import candidate is `texture-candidate.heic`. `control.heic` contains the same encoded primary image without the editing resources. `final-file-mattify-preview.heic` is a baked preview, rather than the import candidate.

The receipt is `acceptance.json`. A passing cloud receipt means native statistics generation, file readback and final-file replay passed. Device activation is recorded separately by the user report above. The native `PhotographicStyleV2` capability, editor eligibility predicate and `supportsSemanticStyleRendering` returned false on the runner. Those observations remain unchanged in the original receipt and do not negate the user's positive device result. The original delivered ZIP and pre-report receipts remain byte-identical.

## Original Apple production entries

| Effect class | Production entry | Real output |
|---|---|---|
| `CMITextureStylesMattify` | `calculateStats` / `process` | face color, highlight/mask ratio |
| `CMITextureStylesUnderEyeBrighten` | `calculateStats` / `process` | left/right eye color, variance, modality |
| `CMITextureStylesSkinSmoothStandalone` | `calculateStats` / `process` | face color, roughness, skip decision |

`PITextureStyleAutoCalculator` computes an edit default; it is not these image-statistics producers. `ANSTFsincAlgorithmV2Dot4` initializes but its installed model fails E5 validation on this runner. Those failures remain in the evidence.

The working sequence is: actual image decode/color conversion → native Vision geometry and masks → native parameter selection → bind IO and full-image regions → initialize the working output image → allocator/setup/prewarm/prepare → calculate statistics → commit/wait → process/collect statistics → finish. The Mattify statistics shader samples `IO.outputImage`; binding an empty output texture produced misleading all-zero results before this dependency was fixed.

Native Mattify exposure controls use EV −1, 0 and +1, with distinct source pixels and distinct statistics. GPU command completion and pixel changes are checked. `FigMetalExecutionStatus` counters alone are not treated as execution evidence.

## Stored resource contract

The 2026 plist contains `TextureStylePostProcessedPeopleData`. Each entry names an **instance** auxiliary image with URI `tag:apple.com,2026:photo:aux:semanticpersoninstances`. Its XMP must contain the matching `fsincMattes:InstanceMaskReferenceKey`. An aggregate `semanticpersonmatte` cannot replace that binding. The harness observes the actual native mask-metadata dictionary in LLDB and verifies one person plus all three statistics groups through `PITextureStyleProcessorKernel.personInputDataFromStillProperties:`.

The ImageIO API type identifiers differ from `auxC` URIs. Directly passing 2026 URIs was ignored; this is not proof that every private 2026 encoder entry is unavailable. Each real scalar mask is encoded through a verified ImageIO scalar-carrier API, then its actual encoded payload and properties are assigned to the final role. The final file is read through the original Neutrino/CMPhoto path. All twelve 2026 semantic roles, legacy hair, the keyed instance, Linear Thumbnail and Style Delta are present.

Resource sources are explicit in `carrier-production.json`:

- Skin, hair, teeth, glasses and the person instance come from native Vision segmentation.
- Face skin and non-face skin are derived from actual skin probabilities and measured face bounds.
- Nose, lip and eyebrow regions are derived from this image's native face landmarks, rather than FSINC inference.
- Hand regions use native hand-pose detection; this fixture yields no detected hands.
- Ear and tattoo protection are explicitly disabled. Their zero masks do not claim absence detection.

Ordinary Styles prerequisites describe a **new SDR identity-edit context**: measured scene/person/skin statistics, an sRGB transfer curve, measured light maps, identity coefficient data, a newly encoded Apple Log thumbnail and a neutral Style Delta grid. They are not recovered camera RAW or original camera tone mapping. The hardware/port/capture fields choose a native tuning profile, and MakerNote 84 declares default edit settings. EXIF camera make/model, ISO, exposure and capture date are not manufactured.

## Final-file validation

One shared inferred geometry and full raw-mask context feeds the original statistics producers and writer. `project_final.py` copies the final carrier's encoded semantic and instance payloads into standalone decoder inputs. Original ImageIO decodes all fourteen scalar inputs. The replay uses those decoded masks, the final primary image and the person/statistics read back from that HEIC. Each effect binds its supported required/optional entries. Fresh Vision results are excluded from the replay inputs. The original native Mattify renderer must complete with finite pixels and a nonzero effect.

Identical container properties are shared and unused descriptors removed; the verified container has 28 properties, below the decoder limit encountered in the compatibility check. The baked preview explicitly converts the Metal row origin to Core Image's image origin. Direct row-order PNGs permit independent orientation and appearance inspection.

The current verified fixture is one 512×512 public NASA portrait with one detected face/person. The native production, write/readback, final-file replay and user-confirmed activation path is established for this delivered candidate. This is not universal-input certification. Multiple-person matching, no-person production, broader orientations/resolutions and full PhotoImaging rendering remain unverified. The user has not yet reported texture/grain or smoothing control effects, save-and-reopen retention, or a comparison against the control file.

## Reproduction and evidence

Run from this repository root on an Apple-silicon macOS 27 machine with Xcode 27:

```sh
bash research/texture-producer-20261020/run.sh /tmp/texture-producer-evidence
```

The manual Actions workflow uses a sparse checkout. Its final preservation step has repository-content write permission solely to create a separate `research/texture-output-<run-id>` branch with newly generated public-image results; it never merges or changes the source branch. Native programs receive no token. The workflow never opens Photos, changes Apple implementations or uploads system model/framework binaries. Generated evidence and all failures are also framed in the job text response. `readback.py` verifies every recovered file's byte length, SHA-256, manifest set and exact source commit. The result branch and import bundle retain their own hashes.

The delivered candidate was generated from source commit `27122d06d29909e13709a13e4768419dc4473c1f` in [run 39370651344](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39370651344). The subsequent activation-status update changes documentation and adds the user's report; it does not rerun or alter the original native evidence. The original [import bundle](https://raw.githubusercontent.com/21Z121Z1/Photographic_Style_Research/e81312a192b68c7984e5c2ff3f436e4c62beb0cd/texture-import-test-20261020.zip) has SHA-256 `0f61ff23a450afe23d370eba8f796d0b223231b30cc5b964f753508a9d10abab`.

Input: [scikit-image's NASA astronaut fixture](https://github.com/scikit-image/scikit-image/blob/v0.25.2/skimage/data/astronaut.png), SHA-256 `88431cd9653ccd539741b555fb0a46b61558b301d4110412b5bc28b5e3ea6cb5`. Its dataset documentation identifies NASA/public-domain provenance.

The person-instance URI/XMP contract was also documented in [Shalielie facts §7](https://github.com/nathanatgit/Shalielie/blob/f95f832eb9f63286eba7b1748d8d9223f168b03a/facts.md). We independently verified the binding through the original native parser; its template landmarks and median person statistics are not used here. HEIF helpers and the identity edit-data contract originate in XDRemux research at `18340989590d451f5676924feb03c70baa503e1a`.

中文结果说明见 [REPORT.zh-CN.md](REPORT.zh-CN.md)。
