import Foundation

public enum RunState: Equatable {
    case idle
    case running
    case succeeded
    case failed(Int32)

    public var isRunning: Bool {
        if case .running = self {
            return true
        }
        return false
    }

    public var label: String {
        switch self {
        case .idle:
            String(localized: "Idle", comment: "Run state label")
        case .running:
            String(localized: "Running", comment: "Run state label")
        case .succeeded:
            String(localized: "Succeeded", comment: "Run state label")
        case .failed(let code):
            String(localized: "Failed (\(code))", comment: "Run state label with exit code")
        }
    }
}

public struct CommandSpec: Equatable, Sendable {
    public var executable: String
    public var arguments: [String]
    public var workingDirectory: URL
    public var environment: [String: String]

    public init(executable: String, arguments: [String], workingDirectory: URL, environment: [String: String]) {
        self.executable = executable
        self.arguments = arguments
        self.workingDirectory = workingDirectory
        self.environment = environment
    }

    public var displayCommand: String {
        ([executable] + arguments).map(Self.shellQuoted).joined(separator: " ")
    }

    private static func shellQuoted(_ value: String) -> String {
        guard value.rangeOfCharacter(from: CharacterSet(charactersIn: " \t\n\"'\\()[]{};&|<>$`")) != nil else {
            return value
        }
        return "'" + value.replacingOccurrences(of: "'", with: "'\\''") + "'"
    }
}

public struct ProcessResult: Equatable, Sendable {
    public var terminationStatus: Int32
    public var standardOutput: String
    public var standardError: String

    public init(terminationStatus: Int32, standardOutput: String, standardError: String) {
        self.terminationStatus = terminationStatus
        self.standardOutput = standardOutput
        self.standardError = standardError
    }
}

public struct RunRecord: Identifiable, Equatable {
    public let id: UUID
    public let date: Date
    public let title: String
    public let command: String
    public let result: ProcessResult

    public init(id: UUID = UUID(), date: Date = Date(), title: String, command: String, result: ProcessResult) {
        self.id = id
        self.date = date
        self.title = title
        self.command = command
        self.result = result
    }
}

public struct AppMessage: Identifiable, Equatable {
    public let id: UUID
    public let date: Date
    public let text: String

    public init(id: UUID = UUID(), date: Date = Date(), text: String) {
        self.id = id
        self.date = date
        self.text = text
    }
}
