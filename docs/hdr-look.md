# Reconstruct a Photographic Styles HDR look

`tools/hdr-look.command` is a standalone launcher for XDRemux's `hdr-look`
command. It uses the same Rust reconstruction and Apple adapter as the macOS
app. It does not implement another image processing pipeline.

Use the paired XDRemux build containing `hdr-look` on Apple Silicon with macOS
27 or newer. Input must be an original HEIC/HEIF with the supported embedded
Photographic Styles data, including its Linear Thumbnail and style metadata.
An ordinary HEIC without that data is reported as a failure.

Place the launcher beside `bin/xdremux` and `bin/xdremux-apple-adapter`, or set
`XDREMUX_CLI` and `XDREMUX_APPLE_ADAPTER` to the corresponding executables.
It also searches the installed XDRemuxApp helper and `PATH`. It does not build
or download anything when run.

Double-click the launcher and type or drag in a photo or folder path. A folder
is processed recursively. From Terminal:

```sh
./tools/hdr-look.command '/path/to/photo.HEIC'
./tools/hdr-look.command '/path/to/folder'
./tools/hdr-look.command '/path/to/folder' --output-dir '/path/to/results' --headroom 4
```

The default is 8× HDR headroom at original resolution. The supported headrooms
are 2×, 4× and 8×. A new `HDR-Look-<id>` directory is created beside the first
input unless `--output-dir` is supplied. Results are flat `.hdr-look.heic`
files with a path-derived suffix to distinguish identical names in different
directories. Only these photos remain in the output directory: no reports,
manifests or EXR intermediates. Status and failures appear in the terminal;
`--json` emits machine-readable results to stdout without saving a sidecar.

Original files and existing destinations are preserved. Generated HDR-look
files and symbolic links encountered during folder discovery are skipped.
A failed photo does not stop the remaining batch; the exit status is nonzero
if any photo fails. Temporary render data is removed after success or failure.

The scene reference is an estimate reconstructed from the original image and
embedded data. The launcher cannot recover detail lost in the thumbnail or
prove a unique inversion of the camera pipeline. Reconstructed HDR output and
native readback are distinct from physical scene truth and Photos editing.

Launcher regression check (no private frameworks needed):

```sh
python3 -m unittest discover -s tests -p test_hdr_look_launcher.py
```
