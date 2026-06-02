import Foundation

public enum RepositoryLocator {
    public static func locate(startingAt startURL: URL? = nil, environment: [String: String] = ProcessInfo.processInfo.environment) -> URL {
        if let configured = environment["STYLEDELTAMAP_REPO_ROOT"], !configured.isEmpty {
            return URL(fileURLWithPath: configured).standardizedFileURL
        }

        // #filePath resolves at compile time to the source tree — walk up from there
        let sourceFile = URL(fileURLWithPath: #filePath).standardizedFileURL
        let sourceCandidate = sourceFile
            .deletingLastPathComponent() // Services/
            .deletingLastPathComponent() // StyleDeltaMapCore/
            .deletingLastPathComponent() // Sources/
            .deletingLastPathComponent() // repo root

        let candidates = [
            startURL,
            sourceCandidate,
            Bundle.main.bundleURL.deletingLastPathComponent().deletingLastPathComponent(),
            URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
        ].compactMap { $0 }

        for candidate in candidates {
            if let found = findRepoRoot(from: candidate) {
                return found
            }
        }
        return URL(fileURLWithPath: FileManager.default.currentDirectoryPath).standardizedFileURL
    }

    public static func findRepoRoot(from url: URL) -> URL? {
        var current = url.standardizedFileURL.path
        let fileManager = FileManager.default

        for _ in 0..<64 {
            let injectTool = (current as NSString).appendingPathComponent("tools/inject_style_family.py")
            let gitDir = (current as NSString).appendingPathComponent(".git")
            if fileManager.fileExists(atPath: injectTool), fileManager.fileExists(atPath: gitDir) {
                return URL(fileURLWithPath: current)
            }
            let parent = (current as NSString).deletingLastPathComponent
            if parent == current {
                return nil
            }
            current = parent
        }
        return nil
    }
}
