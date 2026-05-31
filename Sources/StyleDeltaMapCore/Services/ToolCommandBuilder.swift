import Foundation

public enum ToolCommandBuilderError: LocalizedError, Equatable {
    case missingField(String)

    public var errorDescription: String? {
        switch self {
        case .missingField(let field):
            "Missing required field: \(field)"
        }
    }
}

public struct ToolCommandBuilder {
    public var environment: ToolEnvironment

    public init(environment: ToolEnvironment) {
        self.environment = environment
    }

    public func directInjection(_ configuration: DirectInjectionConfiguration) throws -> CommandSpec {
        let styleDonor = firstNonEmpty(configuration.styleDonor, environment.path("artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic"))
        let template = firstNonEmpty(configuration.templateHEIC, environment.path("Apple_Native_Samples/IMG_0032.HEIC"))
        let output = firstNonEmpty(configuration.outputHEIC, environment.defaultOutputPath(fileName: "style_injected.heic"))

        guard !styleDonor.isEmpty else { throw ToolCommandBuilderError.missingField("Style donor") }
        guard !output.isEmpty else { throw ToolCommandBuilderError.missingField("Output HEIC") }

        var args = [
            "tools/inject_style_family.py",
            "--style-donor", styleDonor,
            "--output", output
        ]

        if configuration.makeBaseWithSips {
            guard !configuration.previewJPEG.isEmpty else { throw ToolCommandBuilderError.missingField("Preview JPEG") }
            args += [
                "--preview-jpeg", configuration.previewJPEG,
                "--make-base-with-sips",
                "--base-size", "\(configuration.baseWidth)x\(configuration.baseHeight)"
            ]
        } else {
            guard !configuration.baseHEIC.isEmpty else { throw ToolCommandBuilderError.missingField("Base HEIC") }
            args += ["--base-heic", configuration.baseHEIC]
            if !configuration.previewJPEG.isEmpty {
                args += ["--preview-jpeg", configuration.previewJPEG]
            }
        }

        if !template.isEmpty {
            args += ["--template", template]
        }
        if !configuration.replacementLinearthumbnailHEVC.isEmpty {
            args += ["--replace-linearthumb-hevc", configuration.replacementLinearthumbnailHEVC]
        }
        if configuration.updateStyleMetadata {
            args.append("--update-style-metadata")
        }
        if configuration.allowDimensionMismatch {
            args.append("--allow-dimension-mismatch")
        }

        return pythonCommand(args)
    }

    public func reconstruction(_ configuration: ReconstructionConfiguration) throws -> CommandSpec {
        switch configuration.mode {
        case .inspectGainMap:
            guard !configuration.gainMap.isEmpty else { throw ToolCommandBuilderError.missingField("Gain map input") }
            var args = [
                "tools/aux_generator.py",
                "inspect-gainmap",
                configuration.gainMap,
                "--gainmap-mode", configuration.gainMapMode
            ]
            appendOptionalOutput("--json", configuration.jsonOutput, to: &args)
            return pythonCommand(args)

        case .linearthumbnailFromGainMap:
            guard !configuration.baseImage.isEmpty else { throw ToolCommandBuilderError.missingField("Base image") }
            guard !configuration.gainMap.isEmpty else { throw ToolCommandBuilderError.missingField("Gain map input") }
            let output = firstNonEmpty(configuration.outputImage, environment.defaultOutputPath(fileName: "linearthumbnail_from_gainmap.png"))
            var args = [
                "tools/aux_generator.py",
                "linearthumbnail-gainmap",
                configuration.baseImage,
                configuration.gainMap,
                "--max-dim", "\(configuration.maxDimension)",
                "--gainmap-mode", configuration.gainMapMode,
                "--output", output
            ]
            appendOptionalOutput("--json", configuration.jsonOutput, to: &args)
            return pythonCommand(args)

        case .linearthumbnailFromDNG:
            guard !configuration.dng.isEmpty else { throw ToolCommandBuilderError.missingField("DNG") }
            let output = firstNonEmpty(configuration.outputImage, environment.defaultOutputPath(fileName: "linearthumbnail_from_dng.png"))
            var args = [
                "tools/aux_generator.py",
                "linearthumbnail-dng",
                configuration.dng,
                "--max-dim", "\(configuration.maxDimension)",
                "--preview-mix", "\(configuration.previewMix)",
                "--output", output
            ]
            if !configuration.preview.isEmpty {
                args += ["--preview", configuration.preview]
            }
            appendOptionalOutput("--json", configuration.jsonOutput, to: &args)
            return pythonCommand(args)

        case .styledeltamapFromGainMap:
            guard !configuration.gainMap.isEmpty else { throw ToolCommandBuilderError.missingField("Gain map input") }
            let output = firstNonEmpty(configuration.outputImage, environment.defaultOutputPath(fileName: "styledeltamap_from_gainmap.png"))
            var args = [
                "tools/aux_generator.py",
                "styledeltamap-gainmap",
                configuration.gainMap,
                "--width", "\(configuration.width)",
                "--height", "\(configuration.height)",
                "--amplitude", "\(configuration.amplitude)",
                "--gainmap-mode", configuration.gainMapMode,
                "--output", output
            ]
            appendOptionalOutput("--json", configuration.jsonOutput, to: &args)
            return pythonCommand(args)
        }
    }

    public func validation(_ configuration: ValidationConfiguration) throws -> CommandSpec {
        guard !configuration.inputHEIC.isEmpty else { throw ToolCommandBuilderError.missingField("Input HEIC") }
        switch configuration.mode {
        case .semantic:
            var args = [
                "tools/semantic_fitter.py",
                configuration.inputHEIC
            ]
            appendOptionalOutput("--json", configuration.jsonOutput, to: &args)
            appendOptionalOutput("--md", configuration.markdownOutput, to: &args)
            appendOptionalOutput("--reference", configuration.referenceHEIC, to: &args)
            appendOptionalOutput("--template", configuration.templateHEIC, to: &args)
            return pythonCommand(args)

        case .heifDump:
            var args = [
                "tools/heif_dump.py",
                configuration.inputHEIC
            ]
            appendOptionalOutput("--json", configuration.jsonOutput, to: &args)
            appendOptionalOutput("--md", configuration.markdownOutput, to: &args)
            return pythonCommand(args)
        }
    }

    private func pythonCommand(_ arguments: [String]) -> CommandSpec {
        CommandSpec(
            executable: environment.processExecutable,
            arguments: environment.pythonArguments(arguments),
            workingDirectory: environment.repositoryRoot,
            environment: [
                "PYTHONUNBUFFERED": "1",
                "STYLEDELTAMAP_REPO_ROOT": environment.repositoryRoot.path
            ]
        )
    }

    private func appendOptionalOutput(_ flag: String, _ value: String, to arguments: inout [String]) {
        if !value.isEmpty {
            arguments += [flag, value]
        }
    }

    private func firstNonEmpty(_ primary: String, _ fallback: String) -> String {
        primary.isEmpty ? fallback : primary
    }
}
