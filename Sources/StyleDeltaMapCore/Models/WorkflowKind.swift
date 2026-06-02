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
            String(localized: "Direct Injection", comment: "Sidebar workflow title")
        case .reconstruction:
            String(localized: "Gain Map / RAW", comment: "Sidebar workflow title")
        case .validation:
            String(localized: "Validation", comment: "Sidebar workflow title")
        case .history:
            String(localized: "Run History", comment: "Sidebar workflow title")
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
            String(localized: "Build a Photos-activating HEIC", comment: "Sidebar workflow subtitle")
        case .reconstruction:
            String(localized: "Generate diagnostic auxiliary rasters", comment: "Sidebar workflow subtitle")
        case .validation:
            String(localized: "Inspect HEIF graph and semantic fit", comment: "Sidebar workflow subtitle")
        case .history:
            String(localized: "Review recent command output", comment: "Sidebar workflow subtitle")
        }
    }
}
