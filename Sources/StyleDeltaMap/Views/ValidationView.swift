import SwiftUI
import StyleDeltaMapCore

struct ValidationView: View {
    @Bindable var store: AppStore

    var body: some View {
        Form {
            Section(String(localized: "Mode", comment: "Section header")) {
                Picker(String(localized: "Operation", comment: "Picker label"), selection: $store.validation.mode) {
                    ForEach(ValidationMode.allCases) { mode in
                        Text(mode.title).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
            }

            Section(String(localized: "Input", comment: "Section header")) {
                PathPickerRow(title: String(localized: "Input HEIC", comment: "Field title"), path: $store.validation.inputHEIC, allowedExtensions: ["heic", "heif", "hif"])
                if store.validation.mode == .semantic {
                    PathPickerRow(title: String(localized: "Reference HEIC", comment: "Field title"), path: $store.validation.referenceHEIC, allowedExtensions: ["heic", "heif", "hif"], placeholder: String(localized: "Optional", comment: "Placeholder text"))
                    PathPickerRow(title: String(localized: "Template HEIC", comment: "Field title"), path: $store.validation.templateHEIC, allowedExtensions: ["heic", "heif", "hif"], placeholder: String(localized: "Optional", comment: "Placeholder text"))
                }
            }

            Section(String(localized: "Outputs", comment: "Section header")) {
                SavePathRow(title: String(localized: "JSON Report", comment: "Field title"), path: $store.validation.jsonOutput, suggestedName: "validation.json", allowedExtension: "json")
                SavePathRow(title: String(localized: "Markdown Report", comment: "Field title"), path: $store.validation.markdownOutput, suggestedName: "validation.md", allowedExtension: "md")
            }
        }
        .formStyle(.grouped)
        .safeAreaInset(edge: .bottom) {
            HStack {
                Button {
                    store.runValidation()
                } label: {
                    Label(String(localized: "Run Validation", comment: "Action button"), systemImage: "play.fill")
                }
                .buttonStyle(.borderedProminent)
                .disabled(store.runState.isRunning)

                Button {
                    FilePanelService.reveal(path: store.validation.jsonOutput.isEmpty ? store.validation.inputHEIC : store.validation.jsonOutput)
                } label: {
                    Label(String(localized: "Reveal Report", comment: "Action button"), systemImage: "magnifyingglass")
                }
                Spacer()
                Text(store.runState.label)
                    .foregroundStyle(.secondary)
            }
            .padding()
            .background(.regularMaterial)
        }
        .navigationTitle(String(localized: "Validation", comment: "Navigation title"))
    }
}
