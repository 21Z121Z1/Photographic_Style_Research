import SwiftUI

struct DirectInjectionView: View {
    @Bindable var store: AppStore

    var body: some View {
        Form {
            Section(String(localized: "Base Image", comment: "Section header")) {
                Toggle(String(localized: "Create base HEIC from preview with sips", comment: "Toggle label"), isOn: $store.directInjection.makeBaseWithSips)
                PathPickerRow(
                    title: String(localized: "Preview JPEG", comment: "Field title"),
                    path: $store.directInjection.previewJPEG,
                    allowedExtensions: ["jpg", "jpeg"],
                    placeholder: String(localized: "Required when creating base with sips", comment: "Placeholder text")
                )
                if !store.directInjection.makeBaseWithSips {
                    PathPickerRow(
                        title: String(localized: "Base HEIC", comment: "Field title"),
                        path: $store.directInjection.baseHEIC,
                        allowedExtensions: ["heic", "heif", "hif"],
                        placeholder: String(localized: "Existing Apple-generated base HEIC", comment: "Placeholder text")
                    )
                }
                HStack {
                    NumericField(title: String(localized: "Base Width", comment: "Field title"), value: $store.directInjection.baseWidth, range: 1...20000)
                    NumericField(title: String(localized: "Base Height", comment: "Field title"), value: $store.directInjection.baseHeight, range: 1...20000)
                }
            }

            Section(String(localized: "Style Family", comment: "Section header")) {
                PathPickerRow(
                    title: String(localized: "Style Donor", comment: "Field title"),
                    path: $store.directInjection.styleDonor,
                    allowedExtensions: ["heic", "heif", "hif"]
                )
                PathPickerRow(
                    title: String(localized: "Template HEIC", comment: "Field title"),
                    path: $store.directInjection.templateHEIC,
                    allowedExtensions: ["heic", "heif", "hif"]
                )
                PathPickerRow(
                    title: String(localized: "Linearthumb HEVC", comment: "Field title"),
                    path: $store.directInjection.replacementLinearthumbnailHEVC,
                    allowedExtensions: ["hevc", "h265", "bin"],
                    placeholder: String(localized: "Optional q=0.45 replacement", comment: "Placeholder text")
                )
            }

            Section(String(localized: "Output", comment: "Section header")) {
                SavePathRow(
                    title: String(localized: "Output HEIC", comment: "Field title"),
                    path: $store.directInjection.outputHEIC,
                    suggestedName: "style_injected.heic",
                    allowedExtension: "heic"
                )
                Toggle(String(localized: "Update style metadata", comment: "Toggle label"), isOn: $store.directInjection.updateStyleMetadata)
                Toggle(String(localized: "Allow dimension mismatch", comment: "Toggle label"), isOn: $store.directInjection.allowDimensionMismatch)
            }
        }
        .formStyle(.grouped)
        .safeAreaInset(edge: .bottom) {
            HStack {
                Button {
                    store.runDirectInjection()
                } label: {
                    Label(String(localized: "Build HEIC", comment: "Action button"), systemImage: "play.fill")
                }
                .buttonStyle(.borderedProminent)
                .disabled(store.runState.isRunning)

                Button {
                    FilePanelService.reveal(path: store.directInjection.outputHEIC)
                } label: {
                    Label(String(localized: "Reveal Output", comment: "Action button"), systemImage: "magnifyingglass")
                }
                .disabled(store.directInjection.outputHEIC.isEmpty)

                Spacer()
                Text(store.runState.label)
                    .foregroundStyle(.secondary)
            }
            .padding()
            .background(.regularMaterial)
        }
        .navigationTitle(String(localized: "Direct Injection", comment: "Navigation title"))
    }
}
