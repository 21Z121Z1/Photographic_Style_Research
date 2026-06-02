import SwiftUI
import StyleDeltaMapCore

struct ReconstructionView: View {
    @Bindable var store: AppStore

    var body: some View {
        Form {
            Section(String(localized: "Mode", comment: "Section header")) {
                Picker(String(localized: "Operation", comment: "Picker label"), selection: $store.reconstruction.mode) {
                    ForEach(ReconstructionMode.allCases) { mode in
                        Text(mode.title).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
            }

            Section(String(localized: "Inputs", comment: "Section header")) {
                switch store.reconstruction.mode {
                case .inspectGainMap:
                    PathPickerRow(title: String(localized: "Gain Map Input", comment: "Field title"), path: $store.reconstruction.gainMap, allowedExtensions: ["heic", "heif", "hif", "jpg", "jpeg", "png", "dng"])
                    gainMapModePicker
                case .linearthumbnailFromGainMap:
                    PathPickerRow(title: String(localized: "Base Image", comment: "Field title"), path: $store.reconstruction.baseImage, allowedExtensions: ["heic", "heif", "hif", "jpg", "jpeg", "png", "dng"])
                    PathPickerRow(title: String(localized: "Gain Map Input", comment: "Field title"), path: $store.reconstruction.gainMap, allowedExtensions: ["heic", "heif", "hif", "jpg", "jpeg", "png", "dng"])
                    gainMapModePicker
                    NumericField(title: String(localized: "Max Dimension", comment: "Field title"), value: $store.reconstruction.maxDimension, range: 128...4096)
                case .linearthumbnailFromDNG:
                    PathPickerRow(title: String(localized: "DNG", comment: "Field title"), path: $store.reconstruction.dng, allowedExtensions: ["dng"])
                    PathPickerRow(title: String(localized: "Preview", comment: "Field title"), path: $store.reconstruction.preview, allowedExtensions: ["jpg", "jpeg", "png"], placeholder: String(localized: "Optional rendered preview", comment: "Placeholder text"))
                    NumericField(title: String(localized: "Max Dimension", comment: "Field title"), value: $store.reconstruction.maxDimension, range: 128...4096)
                    HStack {
                        Text(String(localized: "Preview Mix", comment: "Field label"))
                            .frame(width: 180, alignment: .trailing)
                            .foregroundStyle(.secondary)
                        Slider(value: $store.reconstruction.previewMix, in: 0...1)
                        Text(store.reconstruction.previewMix, format: .number.precision(.fractionLength(2)))
                            .frame(width: 44, alignment: .trailing)
                    }
                case .styledeltamapFromGainMap:
                    PathPickerRow(title: String(localized: "Gain Map Input", comment: "Field title"), path: $store.reconstruction.gainMap, allowedExtensions: ["heic", "heif", "hif", "jpg", "jpeg", "png", "dng"])
                    gainMapModePicker
                    NumericField(title: String(localized: "Width", comment: "Field title"), value: $store.reconstruction.width, range: 64...8192)
                    NumericField(title: String(localized: "Height", comment: "Field title"), value: $store.reconstruction.height, range: 64...8192)
                    HStack {
                        Text(String(localized: "Amplitude", comment: "Field label"))
                            .frame(width: 180, alignment: .trailing)
                            .foregroundStyle(.secondary)
                        Slider(value: $store.reconstruction.amplitude, in: 0...32)
                        Text(store.reconstruction.amplitude, format: .number.precision(.fractionLength(1)))
                            .frame(width: 44, alignment: .trailing)
                    }
                }
            }

            Section(String(localized: "Outputs", comment: "Section header")) {
                if store.reconstruction.mode == .inspectGainMap {
                    SavePathRow(title: String(localized: "JSON Report", comment: "Field title"), path: $store.reconstruction.jsonOutput, suggestedName: "gainmap_inspect.json", allowedExtension: "json")
                } else {
                    SavePathRow(title: String(localized: "Output PNG", comment: "Field title"), path: $store.reconstruction.outputImage, suggestedName: suggestedOutputName, allowedExtension: "png")
                    SavePathRow(title: String(localized: "Stats JSON", comment: "Field title"), path: $store.reconstruction.jsonOutput, suggestedName: "aux_stats.json", allowedExtension: "json")
                }
            }
        }
        .formStyle(.grouped)
        .safeAreaInset(edge: .bottom) {
            HStack {
                Button {
                    store.runReconstruction()
                } label: {
                    Label(String(localized: "Run Reconstruction", comment: "Action button"), systemImage: "play.fill")
                }
                .buttonStyle(.borderedProminent)
                .disabled(store.runState.isRunning)

                Button {
                    FilePanelService.reveal(path: store.reconstruction.outputImage.isEmpty ? store.reconstruction.jsonOutput : store.reconstruction.outputImage)
                } label: {
                    Label(String(localized: "Reveal Output", comment: "Action button"), systemImage: "magnifyingglass")
                }
                Spacer()
                Text(store.runState.label)
                    .foregroundStyle(.secondary)
            }
            .padding()
            .background(.regularMaterial)
        }
        .navigationTitle(String(localized: "Gain Map / RAW", comment: "Navigation title"))
    }

    private var gainMapModePicker: some View {
        Picker(String(localized: "Gain Map Mode", comment: "Picker label"), selection: $store.reconstruction.gainMapMode) {
            Text(String(localized: "Auto", comment: "Picker option")).tag("auto")
            Text(String(localized: "OPPO", comment: "Picker option")).tag("oppo")
            Text(String(localized: "MPF", comment: "Picker option")).tag("mpf")
            Text(String(localized: "Image", comment: "Picker option")).tag("image")
        }
    }

    private var suggestedOutputName: String {
        switch store.reconstruction.mode {
        case .inspectGainMap:
            "gainmap_inspect.json"
        case .linearthumbnailFromGainMap:
            "linearthumbnail_from_gainmap.png"
        case .linearthumbnailFromDNG:
            "linearthumbnail_from_dng.png"
        case .styledeltamapFromGainMap:
            "styledeltamap_from_gainmap.png"
        }
    }
}
