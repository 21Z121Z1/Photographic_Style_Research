import SwiftUI
import StyleDeltaMapCore

struct ValidationView: View {
    @Bindable var store: AppStore

    var body: some View {
        Form {
            Section("Mode") {
                Picker("Operation", selection: $store.validation.mode) {
                    ForEach(ValidationMode.allCases) { mode in
                        Text(mode.title).tag(mode)
                    }
                }
                .pickerStyle(.segmented)
            }

            Section("Input") {
                PathPickerRow(title: "Input HEIC", path: $store.validation.inputHEIC, allowedExtensions: ["heic", "heif", "hif"])
                if store.validation.mode == .semantic {
                    PathPickerRow(title: "Reference HEIC", path: $store.validation.referenceHEIC, allowedExtensions: ["heic", "heif", "hif"], placeholder: "Optional")
                    PathPickerRow(title: "Template HEIC", path: $store.validation.templateHEIC, allowedExtensions: ["heic", "heif", "hif"], placeholder: "Optional")
                }
            }

            Section("Outputs") {
                SavePathRow(title: "JSON Report", path: $store.validation.jsonOutput, suggestedName: "validation.json", allowedExtension: "json")
                SavePathRow(title: "Markdown Report", path: $store.validation.markdownOutput, suggestedName: "validation.md", allowedExtension: "md")
            }
        }
        .formStyle(.grouped)
        .safeAreaInset(edge: .bottom) {
            HStack {
                Button {
                    store.runValidation()
                } label: {
                    Label("Run Validation", systemImage: "play.fill")
                }
                .buttonStyle(.borderedProminent)
                .disabled(store.runState.isRunning)

                Button {
                    FilePanelService.reveal(path: store.validation.jsonOutput.isEmpty ? store.validation.inputHEIC : store.validation.jsonOutput)
                } label: {
                    Label("Reveal Report", systemImage: "magnifyingglass")
                }
                Spacer()
                Text(store.runState.label)
                    .foregroundStyle(.secondary)
            }
            .padding()
            .background(.regularMaterial)
        }
        .navigationTitle("Validation")
    }
}
