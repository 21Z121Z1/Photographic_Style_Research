# XDRemux Texture native research — 2026-10-19—20

This independent PSR branch carries native probes for XDRemux. It does not merge or publish a product Texture feature. Swift calls Apple APIs; Rust owns synthetic charts, derived diagnostic data and pixel statistics. No Apple implementation or residency-policy patches are applied.

## Deliverables and exact sources

- XDRemux research/texture-native-20261019: **18340989590d451f5676924feb03c70baa503e1a**
- Native probe execution source: **84f2c8309c5d778d911148aacbeaae3aff3bdd4f**; the probe source files remain unchanged.
- [Chinese REPORT](https://github.com/21Z121Z1/XDRemux/blob/18340989590d451f5676924feb03c70baa503e1a/research/texture-style/REPORT.zh-CN.md)
- [claims.json](https://github.com/21Z121Z1/XDRemux/blob/18340989590d451f5676924feb03c70baa503e1a/research/texture-style/claims.json)
- [NATIVE_TODO](https://github.com/21Z121Z1/XDRemux/blob/18340989590d451f5676924feb03c70baa503e1a/research/texture-style/NATIVE_TODO.md)
- [Evidence graph](https://github.com/21Z121Z1/XDRemux/blob/18340989590d451f5676924feb03c70baa503e1a/research/texture-style/evidence-graph.json)
- [21 actual native job logs /147 hash-checked native JSON payloads](https://github.com/21Z121Z1/XDRemux/blob/18340989590d451f5676924feb03c70baa503e1a/research/texture-style/evidence/native-readback-index.json)

## Actual outcomes

The safe XDRemux API refuses unsupported new capture facts and preserves existing opaque carriers byte for byte. The old fixed-camera/MakerNote/twelve-role fabrication defect was reproduced.

On macOS27.0.1 /26A434, Xcode27.0 /27A266a, SDK27.0, the Texture metadata parser accepts four metadata controls and rejects an empty dictionary with NUError3. macOS26.6.2 /25G83, Xcode26.6 /17F113, SDK26.5 lacks the Texture classes. Parsing is metadata-only; missing hardware and version999 also return nonnil and do not prove complete image eligibility.

Native settings factories create30 controls without image input. Effect-specific dependencies differ. The native13-name input list includes hairMatte. Bloom's empty required channel set does not establish the kernel's fixed input-layout contract.

Twelve CC0 JPEG/HEIC/SDR/PQ/AdaptiveHDR native codec cases pass. Four ordinary Styles conversions fail at primary dimg or scaffold tmap conditions before final assembly; batch is unexecuted.

Real native Bloom render attempts at intensity0/0.5/1 abort. The unpatched native diagnostic progresses from Missing arguments to Unexpected number of inputs after a new Rust-derived2023 semantic diagnostic is accepted. _textureCache initialization assertion and nil CMI processor initialization are recorded. There are no valid rendered pixels or proven parameter effects. This does not establish universal hardware impossibility.

A complete arbitrary-image Texture producer, complete-file Apple eligibility, original camera reconstruction and iPhone Photos activation remain unverified. Private camera positives and device/UI access are absent. Artifact ZIP bytes remain unverified after the prior container's download tunnel403; permitted log JSON was read back and hash-checked.

## Exact-HEAD limited acceptance

[Final successful run39359955336](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/39359955336), job118423568159, executed PSR source **59f84b9090dc2b6366d8cc0c26fd86e02b8a53a3** against XDRemux **18340989590d451f5676924feb03c70baa503e1a** and base **f8fcf2067c506e87665e9ea113324db1a57d4cf7**.

All five declared checks pass, the tracked checkout is clean, diff check passes, HEAD is unchanged, and agent_completion_gate.py verify reports PASS for the same exact SHA.

- Six transport/provenance regressions.
- Functional opaque transport, full27-test HEIF crate, clippy and actual CLI build.
- Four evidence-reader regressions including tamper, path/truncation and raw CR preservation.
- Recheck21 complete logs,18 manifests and147 actual native JSON payloads.
- Seventeen public documentation and Rust/Apple ownership checks.

[Exact receipt](offline-acceptance/run39359955336/receipt.json), [runner manifest](offline-acceptance/run39359955336/manifest.json), [readback](offline-acceptance/run39359955336/readback.json), [complete job log](offline-acceptance/run39359955336/job118423568159.log).

Receipt SHA256: **fccbff872700f280bd7fd38c29fe78c27cc5eb52bba2479ec9e7e46109e7a32e** (28177 bytes). The actual receipt bytes match the runner manifest. This validates offline transport and text evidence only; it excludes the failed ordinary native conversion path, complete Texture generation/rendering and Photos activation.

Earlier run39359488357 passed every declared test but failed the built-in diff check on native trailing whitespace. Its failure receipt is retained. The narrow XD .gitattributes setting preserves the source log bytes; no source logs were stripped to make the gate green. Run39359818678 then passed the exact same final XD SHA and receipt verification. The last run also disables Rust cache metadata in the non-Cargo PSR root.

## Reproduction and cleanup

The temporary active workflow has been removed from this branch after readback. Nothing is merged into master or other research branches. No secrets, releases or branches are removed.

- native-workflow.example.yml archives the native experiment as manual dispatch only, with1-day text artifacts and the original pinned XD source0a462134.
- offline-workflow.example.yml archives the exact final acceptance as manual dispatch only.
- To rerun, restore the chosen example into this own branch's .github/workflows and use workflow_dispatch. Do not add a push-triggered native probe or run native recomputation in XDRemux.
- native_probe.swift, native_images.swift, run_metadata_matrix.py, run_bloom_matrix.py, run_product_matrix.py, semantic_control.rs and buffer_facts.rs retain the actual entrypoints. No user media is required.
- For offline evidence checks, run the scripts and committed plan in the linked XDRemux report.

The newly selected local execution environment still reports starting/no usable environment. Old local uncommitted files were not inspected or overwritten during remote recovery. Preserve that index and those files when the environment returns, then compare against the final remote source. This is a pending local recovery step, not evidence of file loss.
