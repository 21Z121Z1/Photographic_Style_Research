import Foundation

public enum WorkflowKind: String, CaseIterable, Identifiable {
    case directInjection
    case reconstruction
    case validation
    case history

    public var id: String { rawValue }

    public var title: String {
        switch self {
        case .directInjection:
            "Direct Injection"
        case .reconstruction:
            "Gain Map / RAW"
        case .validation:
            "Validation"
        case .history:
            "Run History"
        }
    }

    public var systemImage: String {
        switch self {
        case .directInjection:
            "wand.and.stars"
        case .reconstruction:
            "waveform.path.ecg.rectangle"
        case .validation:
            "checkmark.seal"
        case .history:
            "clock.arrow.circlepath"
        }
    }

    public var subtitle: String {
        switch self {
        case .directInjection:
            "Build a Photos-activating HEIC"
        case .reconstruction:
            "Generate diagnostic auxiliary rasters"
        case .validation:
            "Inspect HEIF graph and semantic fit"
        case .history:
            "Review recent command output"
        }
    }
}
