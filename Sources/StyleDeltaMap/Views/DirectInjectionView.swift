import SwiftUI

struct DirectInjectionView: View {
    @Bindable var store: AppStore

    var body: some View {
        Form {
            Section("Base Image") {
                Toggle("Create base HEIC from preview with sips", isOn: $store.directInjection.makeBaseWithSips)
                PathPickerRow(
                    title: "Preview JPEG",
                    path: $store.directInjection.previewJPEG,
                    allowedExtensions: ["jpg", "jpeg"],
                    placeholder: "Required when creating base with sips"
                )
                if !store.directInjection.makeBaseWithSips {
                    PathPickerRow(
                        title: "Base HEIC",
                        path: $store.directInjection.baseHEIC,
                        allowedExtensions: ["heic", "heif", "hif"],
                        placeholder: "Existing Apple-generated base HEIC"
                    )
                }
                HStack {
                    NumericField(title: "Base Width", value: $store.directInjection.baseWidth, range: 1...20000)
                    NumericField(title: "Base Height", value: $store.directInjection.baseHeight, range: 1...20000)
                }
            }

            Section("Style Family") {
                PathPickerRow(
                    title: "Style Donor",
                    path: $store.directInjection.styleDonor,
                    allowedExtensions: ["heic", "heif", "hif"]
                )
                PathPickerRow(
                    title: "Template HEIC",
                    path: $store.directInjection.templateHEIC,
                    allowedExtensions: ["heic", "heif", "hif"]
                )
                PathPickerRow(
                    title: "Linearthumb HEVC",
                    path: $store.directInjection.replacementLinearthumbnailHEVC,
                    allowedExtensions: ["hevc", "h265", "bin"],
                    placeholder: "Optional q=0.45 replacement"
                )
            }

            Section("Output") {
                SavePathRow(
                    title: "Output HEIC",
                    path: $store.directInjection.outputHEIC,
                    suggestedName: "style_injected.heic",
                    allowedExtension: "heic"
                )
                Toggle("Update style metadata", isOn: $store.directInjection.updateStyleMetadata)
                Toggle("Allow dimension mismatch", isOn: $store.directInjection.allowDimensionMismatch)
            }
        }
        .formStyle(.grouped)
        .safeAreaInset(edge: .bottom) {
            HStack {
                Button {
                    store.runDirectInjection()
                } label: {
                    Label("Build HEIC", systemImage: "play.fill")
                }
                .buttonStyle(.borderedProminent)
                .disabled(store.runState.isRunning)

                Button {
                    FilePanelService.reveal(path: store.directInjection.outputHEIC)
                } label: {
                    Label("Reveal Output", systemImage: "magnifyingglass")
                }
                .disabled(store.directInjection.outputHEIC.isEmpty)

                Spacer()
                Text(store.runState.label)
                    .foregroundStyle(.secondary)
            }
            .padding()
            .background(.regularMaterial)
        }
        .navigationTitle("Direct Injection")
    }
}
