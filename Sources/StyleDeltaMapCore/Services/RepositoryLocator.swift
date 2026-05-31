import Foundation

public enum RepositoryLocator {
    public static func locate(startingAt startURL: URL? = nil, environment: [String: String] = ProcessInfo.processInfo.environment) -> URL {
        if let configured = environment["STYLEDELTAMAP_REPO_ROOT"], !configured.isEmpty {
            return URL(fileURLWithPath: configured).standardizedFileURL
        }

        let candidates = [
            startURL,
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
        var current = url.standardizedFileURL
        let fileManager = FileManager.default

        while true {
            let injectTool = current.appendingPathComponent("tools/inject_style_family.py").path
            let gitDir = current.appendingPathComponent(".git").path
            if fileManager.fileExists(atPath: injectTool), fileManager.fileExists(atPath: gitDir) {
                return current
            }
            let parent = current.deletingLastPathComponent()
            if parent.path == current.path {
                return nil
            }
            current = parent
        }
    }
}
