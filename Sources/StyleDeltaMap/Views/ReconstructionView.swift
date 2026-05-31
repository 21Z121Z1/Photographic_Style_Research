import SwiftUI
import StyleDeltaMapCore

struct ReconstructionView: View {
    @Bindable var store: AppStore

    var body: some View {
        Form {
            Section("Mode") {
                Picker("Operation", selection: $store.reconstruction.mode) {
                    ForEach(ReconstructionMode.allCases) { mode in
                        Text(mode.title).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
            }

            Section("Inputs") {
                switch store.reconstruction.mode {
                case .inspectGainMap:
                    PathPickerRow(title: "Gain Map Input", path: $store.reconstruction.gainMap, allowedExtensions: ["heic", "heif", "hif", "jpg", "jpeg", "png", "dng"])
                    gainMapModePicker
                case .linearthumbnailFromGainMap:
                    PathPickerRow(title: "Base Image", path: $store.reconstruction.baseImage, allowedExtensions: ["heic", "heif", "hif", "jpg", "jpeg", "png", "dng"])
                    PathPickerRow(title: "Gain Map Input", path: $store.reconstruction.gainMap, allowedExtensions: ["heic", "heif", "hif", "jpg", "jpeg", "png", "dng"])
                    gainMapModePicker
                    NumericField(title: "Max Dimension", value: $store.reconstruction.maxDimension, range: 128...4096)
                case .linearthumbnailFromDNG:
                    PathPickerRow(title: "DNG", path: $store.reconstruction.dng, allowedExtensions: ["dng"])
                    PathPickerRow(title: "Preview", path: $store.reconstruction.preview, allowedExtensions: ["jpg", "jpeg", "png"], placeholder: "Optional rendered preview")
                    NumericField(title: "Max Dimension", value: $store.reconstruction.maxDimension, range: 128...4096)
                    HStack {
                        Text("Preview Mix")
                            .frame(width: 180, alignment: .trailing)
                            .foregroundStyle(.secondary)
                        Slider(value: $store.reconstruction.previewMix, in: 0...1)
                        Text(store.reconstruction.previewMix, format: .number.precision(.fractionLength(2)))
                            .frame(width: 44, alignment: .trailing)
                    }
                case .styledeltamapFromGainMap:
                    PathPickerRow(title: "Gain Map Input", path: $store.reconstruction.gainMap, allowedExtensions: ["heic", "heif", "hif", "jpg", "jpeg", "png", "dng"])
                    gainMapModePicker
                    NumericField(title: "Width", value: $store.reconstruction.width, range: 64...8192)
                    NumericField(title: "Height", value: $store.reconstruction.height, range: 64...8192)
                    HStack {
                        Text("Amplitude")
                            .frame(width: 180, alignment: .trailing)
                            .foregroundStyle(.secondary)
                        Slider(value: $store.reconstruction.amplitude, in: 0...32)
                        Text(store.reconstruction.amplitude, format: .number.precision(.fractionLength(1)))
                            .frame(width: 44, alignment: .trailing)
                    }
                }
            }

            Section("Outputs") {
                if store.reconstruction.mode == .inspectGainMap {
                    SavePathRow(title: "JSON Report", path: $store.reconstruction.jsonOutput, suggestedName: "gainmap_inspect.json", allowedExtension: "json")
                } else {
                    SavePathRow(title: "Output PNG", path: $store.reconstruction.outputImage, suggestedName: suggestedOutputName, allowedExtension: "png")
                    SavePathRow(title: "Stats JSON", path: $store.reconstruction.jsonOutput, suggestedName: "aux_stats.json", allowedExtension: "json")
                }
            }
        }
        .formStyle(.grouped)
        .safeAreaInset(edge: .bottom) {
            HStack {
                Button {
                    store.runReconstruction()
                } label: {
                    Label("Run Reconstruction", systemImage: "play.fill")
                }
                .buttonStyle(.borderedProminent)
                .disabled(store.runState.isRunning)

                Button {
                    FilePanelService.reveal(path: store.reconstruction.outputImage.isEmpty ? store.reconstruction.jsonOutput : store.reconstruction.outputImage)
                } label: {
                    Label("Reveal Output", systemImage: "magnifyingglass")
                }
                Spacer()
                Text(store.runState.label)
                    .foregroundStyle(.secondary)
            }
            .padding()
            .background(.regularMaterial)
        }
        .navigationTitle("Gain Map / RAW")
    }

    private var gainMapModePicker: some View {
        Picker("Gain Map Mode", selection: $store.reconstruction.gainMapMode) {
            Text("Auto").tag("auto")
            Text("OPPO").tag("oppo")
            Text("MPF").tag("mpf")
            Text("Image").tag("image")
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
