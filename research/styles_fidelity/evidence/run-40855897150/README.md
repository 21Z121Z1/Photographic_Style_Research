# c/d isolation, joint calibration and final HDR Texture

[Native run](https://github.com/21Z121Z1/Photographic_Style_Research/actions/runs/40855897150) measured research source `4438d48` and product `cf1e790` with the existing isolated producer patch. Raw reports and source binding are retained beside this file. All 35 portable regressions, 105+2 engine tests, native Tone comparison and Texture replay passed. The unrelated firmware-reference job was intentionally skipped.

| Source-generated candidate | Calibration RMSE reduction | Holdout RMSE reduction |
| --- | ---: | ---: |
| c only | 9.64% | 6.09% |
| d only | -0.59% | 0.83% |
| c+d | 9.40% | 7.29% |
| joint exposure/gain + c+d | 16.65% | 10.11% |

The metric averages Tone -0.5 and +0.5. These are the same previously exposed public scene split, not a newly collected unseen dataset. Candidate c/d combinations use no original resources. Original brightness-bundle and full-input substitutions are diagnostic only; both reproduce all three reference Tone points exactly on all three photos.

Replacing only d increases negative-Tone RMSE on all three photos: 1.25%, 0.36%, 1.15%. Replacing only c changes it by -1.13%, +5.42%, +1.41%. Thus d contributes to the regression but does not explain it alone. The controlled variants preserve the other map, curve, exposure and thumbnail; report hashes verify that isolation.

The joint candidate fixes both exposure/gain scales at 0.75 and retains the default 10.4 baseline cap. It regenerates the complete resource set before reading reference resources. Negative-Tone RMSE changes by +0.31%, -8.17%, +0.14%. Despite its lower mean error, negative maximum error rises from 0.0947265625 to 0.11181640625 on IMG_2604 (+18.04%), and from 0.146484375 to 0.16064453125 on holdout IMG_2608 (+9.67%). No candidate is promoted and no product default changes.

Neutral Tone and both Color controls have zero error for all variants. The nine regenerated SDR/HDR base comparisons are exact. Full-brightness closure identifies a coupled brightness-resource mismatch for this forward consumer; it does not certify the full engine, reversal or Photos save/reopen.

Texture replay completed twelve calls on one final encoded HDR product: Mattify, UnderEyeBrighten and SkinSmoothStandalone, each in SDR/HDR with stored/recomputed statistics. Its measured HDR working peak is 2.4135677814483643. Stored/recomputed SDR outputs match exactly. HDR maximum differences are respectively 0.07861328125, 0.007568359375 and 0.016845703125. These differences do not prove that recomputed HDR statistics are more correct. The input domain must be matched to the native caller.

The Texture control depicts mannequins and uses 1024-edge analysis with fixed Studio tuning. Human skin, full-resolution effect behavior, preset combinations, full-engine reversal and capture-time pre-LTM data remain unverified. Next work should bind the actual decoded thumbnail, exposure/gain and GTC sampling domain, rather than applying another unobserved gain or adding metadata fields.
