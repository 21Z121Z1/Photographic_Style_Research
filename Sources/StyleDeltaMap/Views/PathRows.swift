import SwiftUI

struct PathPickerRow: View {
    let title: String
    @Binding var path: String
    var allowedExtensions: [String]
    var placeholder: String = ""

    var body: some View {
        HStack {
            Text(title)
                .frame(width: 180, alignment: .trailing)
                .foregroundStyle(.secondary)
            TextField(placeholder, text: $path)
                .textFieldStyle(.roundedBorder)
            Button {
                if let selected = FilePanelService.chooseFile(allowedExtensions: allowedExtensions) {
                    path = selected
                }
            } label: {
                Image(systemName: "folder")
            }
            .help(String(localized: "Choose \(title)", comment: "File picker tooltip"))
        }
    }
}

struct DirectoryPickerRow: View {
    let title: String
    @Binding var path: String

    var body: some View {
        HStack {
            Text(title)
                .frame(width: 180, alignment: .trailing)
                .foregroundStyle(.secondary)
            TextField("", text: $path)
                .textFieldStyle(.roundedBorder)
            Button {
                if let selected = FilePanelService.chooseDirectory() {
                    path = selected
                }
            } label: {
                Image(systemName: "folder")
            }
            .help(String(localized: "Choose \(title)", comment: "File picker tooltip"))
        }
    }
}

struct SavePathRow: View {
    let title: String
    @Binding var path: String
    var suggestedName: String
    var allowedExtension: String

    var body: some View {
        HStack {
            Text(title)
                .frame(width: 180, alignment: .trailing)
                .foregroundStyle(.secondary)
            TextField("", text: $path)
                .textFieldStyle(.roundedBorder)
            Button {
                if let selected = FilePanelService.chooseSavePath(
                    suggestedName: suggestedName,
                    allowedExtension: allowedExtension
                ) {
                    path = selected
                }
            } label: {
                Image(systemName: "square.and.arrow.down")
            }
            .help(String(localized: "Choose output path", comment: "Save path tooltip"))
        }
    }
}

struct NumericField: View {
    let title: String
    @Binding var value: Int
    var range: ClosedRange<Int>

    var body: some View {
        HStack {
            Text(title)
                .frame(width: 180, alignment: .trailing)
                .foregroundStyle(.secondary)
            Stepper(value: $value, in: range) {
                TextField(title, value: $value, format: .number)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 90)
            }
            Spacer()
        }
    }
}
