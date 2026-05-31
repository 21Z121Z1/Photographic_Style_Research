import Foundation
import XCTest
@testable import StyleDeltaMapCore

final class ProcessRunnerTests: XCTestCase {
    func testRunsEcho() async throws {
        let command = CommandSpec(
            executable: "/bin/echo",
            arguments: ["style", "delta"],
            workingDirectory: URL(fileURLWithPath: "/tmp"),
            environment: [:]
        )

        let result = try await ProcessRunner().run(command)

        XCTAssertEqual(result.terminationStatus, 0)
        XCTAssertEqual(result.standardOutput.trimmingCharacters(in: .whitespacesAndNewlines), "style delta")
        XCTAssertEqual(result.standardError, "")
    }
}
