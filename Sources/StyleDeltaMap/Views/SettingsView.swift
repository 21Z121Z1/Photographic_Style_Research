import SwiftUI

struct SettingsView: View {
    @Bindable var store: AppStore

    var body: some View {
        Form {
            Section(String(localized: "Tooling", comment: "Section header")) {
                DirectoryPickerRow(title: String(localized: "Repository Root", comment: "Field title"), path: $store.preferences.repositoryRoot)
                PathPickerRow(
                    title: String(localized: "Python", comment: "Field title"),
                    path: $store.preferences.pythonExecutable,
                    allowedExtensions: [],
                    placeholder: String(localized: "Leave empty to use STYLEDELTAMAP_PYTHON or python3", comment: "Placeholder text")
                )
                DirectoryPickerRow(title: String(localized: "Output Directory", comment: "Field title"), path: $store.preferences.outputDirectory)
            }

            Section(String(localized: "Defaults", comment: "Section header")) {
                PathPickerRow(title: String(localized: "Style Donor", comment: "Field title"), path: $store.preferences.defaultStyleDonor, allowedExtensions: ["heic", "heif", "hif"])
                PathPickerRow(title: String(localized: "Template HEIC", comment: "Field title"), path: $store.preferences.defaultTemplateHEIC, allowedExtensions: ["heic", "heif", "hif"])
                Button(String(localized: "Apply Defaults To Workflows", comment: "Button label")) {
                    store.applyDefaults()
                }
            }
        }
        .formStyle(.grouped)
        .padding()
        .frame(width: 760, height: 360)
    }
}
