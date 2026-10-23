# macOS validation app

The SwiftUI application lets a user select Validation, choose an input HEIC and output paths, then run a structural or semantic report.

## Sub-features

- `app-validation-entry` opens the Validation sidebar workflow.
- `app-input-output` selects Input HEIC, JSON Report and Markdown Report paths.
- `app-run-report` runs validation and reveals the resulting report.

## How to get to it (user POV)

Launch StyleDeltaMap on macOS 14 or later. Select Validation, select Operation, choose Input HEIC and report paths, then choose Run Validation. Reveal Report opens the chosen report location.

## Driving it with verify.py

Preconditions:

- A macOS host, Swift 6 toolchain and an owned application instance are available.
- A synthetic HEIF candidate and fresh output paths are authorized.
- A UI automation driver with accessibility access is available for that owned instance.

- **Build.** Run `swift build` from the repository root. Launch the resulting StyleDeltaMap executable in an owned instance and record its actual PID. Do not call the repository build-and-run script during shared verification because it currently kills all processes named StyleDeltaMap.
- **Drive.** Use the UI driver's accessibility handles for Validation, Operation, Input HEIC, JSON Report, Markdown Report, Run Validation and Reveal Report. Capture the action sequence, app identity and saved report values.
- **Prove side effects.** Reopen the reports through the file path shown by Reveal Report, verify the input SHA is unchanged, and retain the app transcript plus screenshots. Compilation alone is not UI proof.
- **Cleanup.** Close only the PID launched by this journey. Keep screenshots and reports.

## Gotchas

- This journey is blocked on Linux and was not executed by the generated skill.
- No UI driver is available in the current session. These source-derived accessibility labels are not a tested automation recipe on macOS.
- The app delegates to tools. A passing tool journey does not prove picker behavior, startup or app-side argument construction.
