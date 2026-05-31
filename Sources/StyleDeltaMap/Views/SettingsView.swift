import SwiftUI

struct SettingsView: View {
    @Bindable var store: AppStore

    var body: some View {
        Form {
            Section("Tooling") {
                DirectoryPickerRow(title: "Repository Root", path: $store.preferences.repositoryRoot)
                PathPickerRow(
                    title: "Python",
                    path: $store.preferences.pythonExecutable,
                    allowedExtensions: [],
                    placeholder: "Leave empty to use STYLEDELTAMAP_PYTHON or python3"
                )
                DirectoryPickerRow(title: "Output Directory", path: $store.preferences.outputDirectory)
            }

            Section("Defaults") {
                PathPickerRow(title: "Style Donor", path: $store.preferences.defaultStyleDonor, allowedExtensions: ["heic", "heif", "hif"])
                PathPickerRow(title: "Template HEIC", path: $store.preferences.defaultTemplateHEIC, allowedExtensions: ["heic", "heif", "hif"])
                Button("Apply Defaults To Workflows") {
                    store.applyDefaults()
                }
            }
        }
        .formStyle(.grouped)
        .padding()
        .frame(width: 760, height: 360)
    }
}
