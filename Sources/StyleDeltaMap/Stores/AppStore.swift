import Foundation
import Observation
import StyleDeltaMapCore

@MainActor
@Observable
final class AppStore {
    var selectedWorkflow: WorkflowKind = .directInjection
    var directInjection = DirectInjectionConfiguration()
    var reconstruction = ReconstructionConfiguration()
    var validation = ValidationConfiguration()
    var preferences: AppPreferences
    var runState: RunState = .idle
    var messages: [AppMessage] = []
    var history: [RunRecord] = []
    var lastCommand: CommandSpec?

    private let runner: ProcessRunner

    init(runner: ProcessRunner = ProcessRunner()) {
        self.runner = runner
        let repo = RepositoryLocator.locate()
        self.preferences = AppPreferences(
            repositoryRoot: repo.path,
            pythonExecutable: ProcessInfo.processInfo.environment["STYLEDELTAMAP_PYTHON"] ?? "",
            outputDirectory: repo.appendingPathComponent("artifacts/app_outputs").path,
            defaultStyleDonor: repo.appendingPathComponent("artifacts/constructed/apple_parity_styledeltamap_v8_vt_linearthumb_q025/apple_parity_styledeltamap_v8_vt_linearthumb_q025.heic").path,
            defaultTemplateHEIC: repo.appendingPathComponent("Apple_Native_Samples/IMG_0032.HEIC").path
        )
        applyDefaults()
    }

    var toolEnvironment: ToolEnvironment {
        ToolEnvironment(preferences: preferences)
    }

    var builder: ToolCommandBuilder {
        ToolCommandBuilder(environment: toolEnvironment)
    }

    func applyDefaults() {
        if directInjection.styleDonor.isEmpty {
            directInjection.styleDonor = preferences.defaultStyleDonor
        }
        if directInjection.templateHEIC.isEmpty {
            directInjection.templateHEIC = preferences.defaultTemplateHEIC
        }
        if validation.templateHEIC.isEmpty {
            validation.templateHEIC = preferences.defaultTemplateHEIC
        }
    }

    func runDirectInjection() {
        run(title: "Direct Injection") {
            try self.builder.directInjection(self.directInjection)
        }
    }

    func runReconstruction() {
        run(title: reconstruction.mode.title) {
            try self.builder.reconstruction(self.reconstruction)
        }
    }

    func runValidation() {
        run(title: validation.mode.title) {
            try self.builder.validation(self.validation)
        }
    }

    func runSelectedWorkflow() {
        switch selectedWorkflow {
        case .directInjection:
            runDirectInjection()
        case .reconstruction:
            runReconstruction()
        case .validation:
            runValidation()
        case .history:
            break
        }
    }

    func clearConsole() {
        messages.removeAll()
    }

    private func run(title: String, build: @escaping () throws -> CommandSpec) {
        guard !runState.isRunning else {
            append(String(localized: "A command is already running.", comment: "Console error message"))
            return
        }

        do {
            let command = try build()
            lastCommand = command
            runState = .running
            append("$ \(command.displayCommand)")

            Task {
                do {
                    let result = try await runner.run(command)
                    complete(title: title, command: command, result: result)
                } catch {
                    let result = ProcessResult(
                        terminationStatus: 1,
                        standardOutput: "",
                        standardError: error.localizedDescription
                    )
                    complete(title: title, command: command, result: result)
                }
            }
        } catch {
            runState = .failed(2)
            append(error.localizedDescription)
        }
    }

    private func complete(title: String, command: CommandSpec, result: ProcessResult) {
        if !result.standardOutput.isEmpty {
            append(result.standardOutput.trimmingCharacters(in: .whitespacesAndNewlines))
        }
        if !result.standardError.isEmpty {
            append(result.standardError.trimmingCharacters(in: .whitespacesAndNewlines))
        }
        runState = result.terminationStatus == 0 ? .succeeded : .failed(result.terminationStatus)
        history.insert(RunRecord(title: title, command: command.displayCommand, result: result), at: 0)
        if history.count > 20 {
            history.removeLast(history.count - 20)
        }
    }

    private func append(_ text: String) {
        guard !text.isEmpty else { return }
        messages.append(AppMessage(text: text))
    }
}
