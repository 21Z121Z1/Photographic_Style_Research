import XCTest
@testable import StyleDeltaMapCore

final class ToolCommandBuilderTests: XCTestCase {
    private func builder() -> ToolCommandBuilder {
        let preferences = AppPreferences(
            repositoryRoot: "/tmp/styledeltamap",
            pythonExecutable: "/usr/bin/python3",
            outputDirectory: "/tmp/styledeltamap/out",
            defaultStyleDonor: "/tmp/styledeltamap/donor.heic",
            defaultTemplateHEIC: "/tmp/styledeltamap/template.heic"
        )
        return ToolCommandBuilder(environment: ToolEnvironment(preferences: preferences, environment: [:]))
    }

    func testDirectInjectionBuildsArgumentArrayWithoutShellInterpolation() throws {
        var config = DirectInjectionConfiguration()
        config.previewJPEG = "/tmp/input preview.jpg"
        config.styleDonor = "/tmp/donor.heic"
        config.templateHEIC = "/tmp/template.heic"
        config.replacementLinearthumbnailHEVC = "/tmp/linear thumbnail.hevc"
        config.outputHEIC = "/tmp/output style.heic"

        let command = try builder().directInjection(config)

        XCTAssertEqual(command.executable, "/usr/bin/python3")
        XCTAssertEqual(command.workingDirectory.path, "/tmp/styledeltamap")
        XCTAssertTrue(command.arguments.contains("tools/inject_style_family.py"))
        XCTAssertTrue(command.arguments.contains("--make-base-with-sips"))
        XCTAssertTrue(command.arguments.contains("/tmp/input preview.jpg"))
        XCTAssertTrue(command.arguments.contains("/tmp/linear thumbnail.hevc"))
        XCTAssertFalse(command.displayCommand.contains("\""))
    }

    func testReconstructionRequiresGainMapInput() {
        var config = ReconstructionConfiguration()
        config.mode = .styledeltamapFromGainMap

        XCTAssertThrowsError(try builder().reconstruction(config)) { error in
            XCTAssertEqual(error as? ToolCommandBuilderError, .missingField("Gain map input"))
        }
    }

    func testValidationBuildsSemanticCommandWithReports() throws {
        var config = ValidationConfiguration()
        config.inputHEIC = "/tmp/candidate.heic"
        config.jsonOutput = "/tmp/report.json"
        config.markdownOutput = "/tmp/report.md"

        let command = try builder().validation(config)

        XCTAssertEqual(command.arguments.prefix(2), ["tools/semantic_fitter.py", "/tmp/candidate.heic"])
        XCTAssertTrue(command.arguments.contains("--json"))
        XCTAssertTrue(command.arguments.contains("/tmp/report.json"))
        XCTAssertTrue(command.arguments.contains("--md"))
        XCTAssertTrue(command.arguments.contains("/tmp/report.md"))
    }
}
