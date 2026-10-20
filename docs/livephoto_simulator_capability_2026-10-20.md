# Live Photo wallpaper gate: GitHub Actions Simulator capability probe

Date: 2026-10-20 (UTC)

## Result

The installed iOS 26.5 Simulator cannot provide a genuine settling-effect decision through `VCPSettlingEffectAnalyzer`. The class exists, but its initializer and analysis completion implementation are stubs. This is a measured limitation of this exact runtime and entrypoint, **not a finding that any particular Live Photo is eligible or ineligible**.

No photo or video was imported, uploaded, or evaluated. No private media was used. A sample matrix was deliberately not run after the capability failure. The original question of physical-device wallpaper eligibility therefore remains unverified.

## Reproducible environment

- GitHub runner: `macos-26`, image `macos-26-arm64/20261013.0424.1`
- Host: macOS 26.6.2 (25G83), ARM64
- Xcode: 26.6 (17F113)
- Latest installed available iOS runtime selected: iOS 26.5 (23F77)
- Simulator device: iPhone 17 Pro
- Metal device: `Apple iOS simulator GPU`
- Both native probe processes exited 0
- iOS 27 was not installed in the inspected runner image, so these results do not establish its behavior

The probe compiles an Objective-C iOS Simulator executable with Apple's SDK, boots the simulator, and runs it using `xcrun simctl spawn`. These are runtime observations, not SDK header assumptions.

## Actual native availability

Successfully loaded: Photos, PhotoLibraryServices, MediaAnalysis, MediaAnalysisServices, PhotoImaging, PhotosUICore, PhotosUIPrivate, PosterKit, PosterBoardServices, WallpaperKit.

Present classes include:

- `PIPosterSettlingEffectLoader`
- `PIParallaxSegmentationItem`
- `PUParallaxLayerStackViewModel`
- `VCPSettlingEffectAnalyzer`
- `VCPVideoMetaLivePhotoMetaAnalyzer`
- `MADService` and `MADServicePrivate`

`PIParallaxSegmentationItem` exposes `isSettlingEffectAvailable`, `settlingEffectStatus`, `settlingEffectGatingDiagnostics`, and related accessors. These accessors alone do not prove that the simulator can generate valid analysis results.

## Decisive implementation evidence

The second run captured bounded, read-only instruction bytes from the actual Objective-C method implementations. ARM64 disassembly was performed afterward with Capstone. Addresses below are offsets relative to the loaded MediaAnalysis image.

### `-[VCPSettlingEffectAnalyzer initWithTimestamps:andTrack:]`

```
0x9418: stp x29, x30, [sp, #-0x10]!
0x941c: mov x29, sp
0x9420: bl #0x387644
0x9424: mov x0, #0
0x9428: ldp x29, x30, [sp], #0x10
0x942c: ret
```

The complete method always returns nil after one call; it does not analyze the supplied timestamps or track. The branch target was not resolved, and no claim is made about its identity.

### `-[VCPSettlingEffectAnalyzer finishAnalysisPass:withStillImageBuffer:]`

```
0x9430: mov w0, #0
0x9434: ret
```

This entire method returns zero without reading its inputs. Treating that status as a successful media-quality or wallpaper-eligibility test would be incorrect.

### `+[VCPSettlingEffectAnalyzer getSettlingEffectTimeRange:withOptions:]`

The complete method only copies a fixed 48-byte global value to the return buffer. It does not read the supplied resource/options. The constant's semantic value was not identified, so it is not described as a valid or invalid time range here.

The class has only these own instance methods: initializer above, completion above, `cancelled`, `setCancelled:`, `adjustedTimeRange`, `processAborted`. Its own ivars are `_processAborted`, `_cancelled`, `_adjustedTimeRange`. The metadata-integrity, still-transition, video-quality and FRC failure state present in the historical device header is absent from this class in this runtime. The base `VCPVideoAnalyzer` does expose inherited methods, but that does not overcome the subclass initializer returning nil.

The PhotoImaging loader methods contain nontrivial code. They are not being labeled stubs. Their existence does not establish an operational analysis backend or a correct physical-device eligibility verdict; that higher-level service path was not exercised.

## Runs and source

- Initial capability run: https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39388950263
- Implementation confirmation run: https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39389714260
- Tested implementation commit: `9086920fdd3b1fa7e753261543f6e3c6309916d0`
- Workflow: `.github/workflows/livephoto-simulator.yml`
- Probe: `tools/livephoto_simulator/probe.m`
- Runner: `tools/livephoto_simulator/run.sh`
- Diagnostic artifact: https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39389714260/artifacts/12249725125
- Artifact expiry: 2026-10-21 08:00:25 UTC (one-day retention)

Both jobs completed successfully. Workflow success means the capability probe completed; it does not mean a Live Photo passed wallpaper eligibility.

Historical class-layout reference, used only to choose what to inspect: https://github.com/MTACS/iOS-17-Runtime-Headers/blob/main/PrivateFrameworks/MediaAnalysis.framework/VCPSettlingEffectAnalyzer.h

## Scope and next evidence needed

All changes are confined to `research/livephoto-simulator-20261020`. No PR, merge, master edit, account permission change, private-media publication, or recurring run was made. The workflow has a 12-minute job limit and one-day artifact retention; it only triggers on changes to its own workflow/probe paths.

This runner remains useful for actual AVFoundation/ImageIO/Photos parsing or import checks, if separately implemented, but those are weaker than the lock-screen motion gate. Establishing the target behavior still requires a non-stub analysis path and positive/negative controls on the relevant physical iOS version. Further matrix runs were stopped rather than presenting import success or stub return values as native eligibility.
