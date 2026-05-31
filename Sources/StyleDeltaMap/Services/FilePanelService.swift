import AppKit
import Foundation
import UniformTypeIdentifiers

@MainActor
enum FilePanelService {
    static func chooseFile(allowedExtensions: [String]) -> String? {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        let contentTypes = allowedExtensions.compactMap { UTType(filenameExtension: $0) }
        if !contentTypes.isEmpty {
            panel.allowedContentTypes = contentTypes
        }
        return panel.runModal() == .OK ? panel.url?.path : nil
    }

    static func chooseDirectory() -> String? {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        return panel.runModal() == .OK ? panel.url?.path : nil
    }

    static func chooseSavePath(suggestedName: String, allowedExtension: String) -> String? {
        let panel = NSSavePanel()
        panel.nameFieldStringValue = suggestedName
        if let contentType = UTType(filenameExtension: allowedExtension) {
            panel.allowedContentTypes = [contentType]
        }
        return panel.runModal() == .OK ? panel.url?.path : nil
    }

    static func reveal(path: String) {
        guard !path.isEmpty else { return }
        NSWorkspace.shared.activateFileViewerSelecting([URL(fileURLWithPath: path)])
    }

    static func openDirectory(path: String) {
        guard !path.isEmpty else { return }
        NSWorkspace.shared.open(URL(fileURLWithPath: path, isDirectory: true))
    }
}
