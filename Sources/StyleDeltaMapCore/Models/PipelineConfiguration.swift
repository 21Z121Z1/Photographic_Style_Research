import Foundation

public struct DirectInjectionConfiguration: Equatable {
    public var previewJPEG: String
    public var baseHEIC: String
    public var makeBaseWithSips: Bool
    public var baseWidth: Int
    public var baseHeight: Int
    public var styleDonor: String
    public var templateHEIC: String
    public var replacementLinearthumbnailHEVC: String
    public var outputHEIC: String
    public var updateStyleMetadata: Bool
    public var allowDimensionMismatch: Bool

    public init(
        previewJPEG: String = "",
        baseHEIC: String = "",
        makeBaseWithSips: Bool = true,
        baseWidth: Int = 4032,
        baseHeight: Int = 3024,
        styleDonor: String = "",
        templateHEIC: String = "",
        replacementLinearthumbnailHEVC: String = "",
        outputHEIC: String = "",
        updateStyleMetadata: Bool = false,
        allowDimensionMismatch: Bool = false
    ) {
        self.previewJPEG = previewJPEG
        self.baseHEIC = baseHEIC
        self.makeBaseWithSips = makeBaseWithSips
        self.baseWidth = baseWidth
        self.baseHeight = baseHeight
        self.styleDonor = styleDonor
        self.templateHEIC = templateHEIC
        self.replacementLinearthumbnailHEVC = replacementLinearthumbnailHEVC
        self.outputHEIC = outputHEIC
        self.updateStyleMetadata = updateStyleMetadata
        self.allowDimensionMismatch = allowDimensionMismatch
    }
}

public enum ReconstructionMode: String, CaseIterable, Identifiable {
    case inspectGainMap
    case linearthumbnailFromGainMap
    case linearthumbnailFromDNG
    case styledeltamapFromGainMap

    public var id: String { rawValue }

    public var title: String {
        switch self {
        case .inspectGainMap:
            "Inspect Gain Map"
        case .linearthumbnailFromGainMap:
            "Linearthumbnail From Gain Map"
        case .linearthumbnailFromDNG:
            "Linearthumbnail From DNG"
        case .styledeltamapFromGainMap:
            "Styledeltamap From Gain Map"
        }
    }
}

public struct ReconstructionConfiguration: Equatable {
    public var mode: ReconstructionMode
    public var baseImage: String
    public var gainMap: String
    public var dng: String
    public var preview: String
    public var outputImage: String
    public var jsonOutput: String
    public var gainMapMode: String
    public var maxDimension: Int
    public var width: Int
    public var height: Int
    public var amplitude: Double
    public var previewMix: Double

    public init(
        mode: ReconstructionMode = .inspectGainMap,
        baseImage: String = "",
        gainMap: String = "",
        dng: String = "",
        preview: String = "",
        outputImage: String = "",
        jsonOutput: String = "",
        gainMapMode: String = "auto",
        maxDimension: Int = 1024,
        width: Int = 720,
        height: Int = 540,
        amplitude: Double = 6.0,
        previewMix: Double = 0.25
    ) {
        self.mode = mode
        self.baseImage = baseImage
        self.gainMap = gainMap
        self.dng = dng
        self.preview = preview
        self.outputImage = outputImage
        self.jsonOutput = jsonOutput
        self.gainMapMode = gainMapMode
        self.maxDimension = maxDimension
        self.width = width
        self.height = height
        self.amplitude = amplitude
        self.previewMix = previewMix
    }
}

public enum ValidationMode: String, CaseIterable, Identifiable {
    case semantic
    case heifDump

    public var id: String { rawValue }

    public var title: String {
        switch self {
        case .semantic:
            "Semantic Fit"
        case .heifDump:
            "HEIF Dump"
        }
    }
}

public struct ValidationConfiguration: Equatable {
    public var mode: ValidationMode
    public var inputHEIC: String
    public var jsonOutput: String
    public var markdownOutput: String
    public var referenceHEIC: String
    public var templateHEIC: String

    public init(
        mode: ValidationMode = .semantic,
        inputHEIC: String = "",
        jsonOutput: String = "",
        markdownOutput: String = "",
        referenceHEIC: String = "",
        templateHEIC: String = ""
    ) {
        self.mode = mode
        self.inputHEIC = inputHEIC
        self.jsonOutput = jsonOutput
        self.markdownOutput = markdownOutput
        self.referenceHEIC = referenceHEIC
        self.templateHEIC = templateHEIC
    }
}

public struct AppPreferences: Equatable {
    public var repositoryRoot: String
    public var pythonExecutable: String
    public var outputDirectory: String
    public var defaultStyleDonor: String
    public var defaultTemplateHEIC: String

    public init(
        repositoryRoot: String = "",
        pythonExecutable: String = "",
        outputDirectory: String = "",
        defaultStyleDonor: String = "",
        defaultTemplateHEIC: String = ""
    ) {
        self.repositoryRoot = repositoryRoot
        self.pythonExecutable = pythonExecutable
        self.outputDirectory = outputDirectory
        self.defaultStyleDonor = defaultStyleDonor
        self.defaultTemplateHEIC = defaultTemplateHEIC
    }
}
