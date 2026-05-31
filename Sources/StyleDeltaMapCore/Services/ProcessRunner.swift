import Foundation

private final class ProcessOutputBuffer: @unchecked Sendable {
    private let lock = NSLock()
    private var data = Data()

    func append(_ chunk: Data) {
        guard !chunk.isEmpty else { return }
        lock.lock()
        data.append(chunk)
        lock.unlock()
    }

    var stringValue: String {
        lock.lock()
        let snapshot = data
        lock.unlock()
        return String(data: snapshot, encoding: .utf8) ?? ""
    }
}

public struct ProcessRunner: Sendable {
    public init() {}

    public func run(_ command: CommandSpec) async throws -> ProcessResult {
        try await withCheckedThrowingContinuation { continuation in
            let process = Process()
            process.executableURL = URL(fileURLWithPath: command.executable)
            process.arguments = command.arguments
            process.currentDirectoryURL = command.workingDirectory
            process.environment = ProcessInfo.processInfo.environment.merging(command.environment) { _, new in new }

            let stdout = Pipe()
            let stderr = Pipe()
            process.standardOutput = stdout
            process.standardError = stderr
            let outputBuffer = ProcessOutputBuffer()
            let errorBuffer = ProcessOutputBuffer()

            stdout.fileHandleForReading.readabilityHandler = { handle in
                outputBuffer.append(handle.availableData)
            }
            stderr.fileHandleForReading.readabilityHandler = { handle in
                errorBuffer.append(handle.availableData)
            }

            process.terminationHandler = { process in
                stdout.fileHandleForReading.readabilityHandler = nil
                stderr.fileHandleForReading.readabilityHandler = nil
                continuation.resume(
                    returning: ProcessResult(
                        terminationStatus: process.terminationStatus,
                        standardOutput: outputBuffer.stringValue,
                        standardError: errorBuffer.stringValue
                    )
                )
            }

            do {
                try process.run()
            } catch {
                stdout.fileHandleForReading.readabilityHandler = nil
                stderr.fileHandleForReading.readabilityHandler = nil
                continuation.resume(throwing: error)
            }
        }
    }
}
