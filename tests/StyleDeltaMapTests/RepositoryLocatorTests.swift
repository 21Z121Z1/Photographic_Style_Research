import Foundation
import XCTest
@testable import StyleDeltaMapCore

final class RepositoryLocatorTests: XCTestCase {
    func testEnvironmentOverrideWins() {
        let located = RepositoryLocator.locate(environment: ["STYLEDELTAMAP_REPO_ROOT": "/tmp/custom-root"])
        XCTAssertEqual(located.path, "/tmp/custom-root")
    }

    func testFindsRepoRootByToolAndGitDirectory() throws {
        let root = URL(fileURLWithPath: NSTemporaryDirectory())
            .appendingPathComponent(UUID().uuidString)
        let nested = root.appendingPathComponent("dist/StyleDeltaMap.app")
        try FileManager.default.createDirectory(
            at: root.appendingPathComponent("tools"),
            withIntermediateDirectories: true
        )
        try FileManager.default.createDirectory(
            at: root.appendingPathComponent(".git"),
            withIntermediateDirectories: true
        )
        try FileManager.default.createDirectory(at: nested, withIntermediateDirectories: true)
        FileManager.default.createFile(
            atPath: root.appendingPathComponent("tools/inject_style_family.py").path,
            contents: Data()
        )
        defer {
            try? FileManager.default.removeItem(at: root)
        }

        XCTAssertEqual(RepositoryLocator.findRepoRoot(from: nested)?.path, root.path)
    }
}
