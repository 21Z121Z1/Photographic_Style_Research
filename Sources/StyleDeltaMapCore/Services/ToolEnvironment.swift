import Foundation

public struct ToolEnvironment: Equatable {
    public var repositoryRoot: URL
    public var pythonExecutable: String
    public var outputDirectory: URL

    public init(preferences: AppPreferences, environment: [String: String] = ProcessInfo.processInfo.environment) {
        if preferences.repositoryRoot.isEmpty {
            self.repositoryRoot = RepositoryLocator.locate(environment: environment)
        } else {
            self.repositoryRoot = URL(fileURLWithPath: preferences.repositoryRoot).standardizedFileURL
        }

        if !preferences.pythonExecutable.isEmpty {
            self.pythonExecutable = preferences.pythonExecutable
        } else if let envPython = environment["STYLEDELTAMAP_PYTHON"], !envPython.isEmpty {
            self.pythonExecutable = envPython
        } else {
            self.pythonExecutable = "python3"
        }

        if preferences.outputDirectory.isEmpty {
            self.outputDirectory = repositoryRoot
                .appendingPathComponent("artifacts")
                .appendingPathComponent("app_outputs")
        } else {
            self.outputDirectory = URL(fileURLWithPath: preferences.outputDirectory).standardizedFileURL
        }
    }

    public var processExecutable: String {
        pythonExecutable.hasPrefix("/") ? pythonExecutable : "/usr/bin/env"
    }

    public func pythonArguments(_ arguments: [String]) -> [String] {
        pythonExecutable.hasPrefix("/") ? arguments : [pythonExecutable] + arguments
    }

    public func path(_ relativePath: String) -> String {
        repositoryRoot.appendingPathComponent(relativePath).path
    }

    public func defaultOutputPath(fileName: String) -> String {
        outputDirectory.appendingPathComponent(fileName).path
    }
}
