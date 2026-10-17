import Foundation
import CoreGraphics
import CoreImage
import CoreVideo
import ImageIO
import UniformTypeIdentifiers
import Photos

struct ProbeResult: Encodable {
    let osVersion: String
    let architecture: String
    let imageIOHEICWrite: Bool
    let imageIOHEICRead: Bool
    let encodedWidth: Int?
    let encodedHeight: Int?
    let coreImageAvailable: Bool
    let ciAppleLogToLinearRegistered: Bool
    let ciAppleLogToLinearStatus: String
    let coreVideoL00h: String
    let photosAuthorization: String
    let photosUnstyledReferenceAvailable: Bool
    let notes: [String]
}

func run() throws {
    guard CommandLine.arguments.count == 3 else {
        fputs("usage: swift mac_photos_capability_probe.swift <report.json> <synthetic.heic>\n", stderr)
        exit(2)
    }
    let reportURL = URL(fileURLWithPath: CommandLine.arguments[1])
    let heicURL = URL(fileURLWithPath: CommandLine.arguments[2])
    try FileManager.default.createDirectory(at: reportURL.deletingLastPathComponent(), withIntermediateDirectories: true)
    try FileManager.default.createDirectory(at: heicURL.deletingLastPathComponent(), withIntermediateDirectories: true)

    let cvType = kCVPixelFormatType_OneComponent16Half
    let chars = [24, 16, 8, 0].map { shift in
        String(UnicodeScalar(UInt8(truncatingIfNeeded: (cvType >> shift) & 0xff)))
    }.joined()

    let colorSpace = CGColorSpace(name: CGColorSpace.sRGB)!
    let width = 32
    let height = 24
    var pixels = [UInt8](repeating: 0, count: width * height * 4)
    for y in 0..<height {
        for x in 0..<width {
            let o = (y * width + x) * 4
            pixels[o] = UInt8(x * 255 / (width - 1))
            pixels[o + 1] = UInt8(y * 255 / (height - 1))
            pixels[o + 2] = 83
            pixels[o + 3] = 255
        }
    }
    let image: CGImage? = pixels.withUnsafeMutableBytes { buffer in
        guard let ctx = CGContext(
            data: buffer.baseAddress, width: width, height: height,
            bitsPerComponent: 8, bytesPerRow: width * 4, space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue
        ) else { return nil }
        return ctx.makeImage()
    }

    var wroteHEIC = false
    var readHEIC = false
    var decodedWidth: Int?
    var decodedHeight: Int?
    var notes: [String] = []
    if let image,
       let destination = CGImageDestinationCreateWithURL(
            heicURL as CFURL, UTType.heic.identifier as CFString, 1, nil
       ) {
        CGImageDestinationAddImage(destination, image, nil)
        wroteHEIC = CGImageDestinationFinalize(destination)
        if wroteHEIC,
           let source = CGImageSourceCreateWithURL(heicURL as CFURL, nil),
           let decoded = CGImageSourceCreateImageAtIndex(source, 0, nil) {
            decodedWidth = decoded.width
            decodedHeight = decoded.height
            readHEIC = decoded.width == width && decoded.height == height
        }
    }
    if !wroteHEIC { notes.append("ImageIO HEIC encoder missing or failed") }
    if !readHEIC { notes.append("ImageIO synthetic HEIC round-trip failed") }

    let context = CIContext(options: [.useSoftwareRenderer: true])
    let testImage = CIImage(color: CIColor(red: 0.25, green: 0.5, blue: 0.75))
        .cropped(to: CGRect(x: 0, y: 0, width: 4, height: 4))
    let coreImageAvailable = context.createCGImage(testImage, from: testImage.extent) != nil
    let filterRegistered = CIFilter(name: "CIAppleLogToLinear") != nil

    let authorization = PHPhotoLibrary.authorizationStatus(for: .readWrite)
    let authorizationText: String
    switch authorization {
    case .notDetermined: authorizationText = "notDetermined"
    case .restricted: authorizationText = "restricted"
    case .denied: authorizationText = "denied"
    case .authorized: authorizationText = "authorized"
    case .limited: authorizationText = "limited"
    @unknown default: authorizationText = "unknown"
    }

    #if arch(arm64)
    let arch = "arm64"
    #elseif arch(x86_64)
    let arch = "x86_64"
    #else
    let arch = "unknown"
    #endif

    notes.append("No real Photos Unstyled reference or iOS 27 private frameworks are provided.")
    notes.append("CI filter registration alone cannot validate Apple's photographic style inverse pipeline.")
    let report = ProbeResult(
        osVersion: ProcessInfo.processInfo.operatingSystemVersionString,
        architecture: arch,
        imageIOHEICWrite: wroteHEIC, imageIOHEICRead: readHEIC,
        encodedWidth: decodedWidth, encodedHeight: decodedHeight,
        coreImageAvailable: coreImageAvailable,
        ciAppleLogToLinearRegistered: filterRegistered,
        ciAppleLogToLinearStatus: filterRegistered ? "registered_unverified" : "not_registered",
        coreVideoL00h: chars, photosAuthorization: authorizationText,
        photosUnstyledReferenceAvailable: false, notes: notes
    )
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let encoded = try encoder.encode(report)
    try encoded.write(to: reportURL)
    print(String(decoding: encoded, as: UTF8.self))

    guard chars == "L00h" else {
        fputs("L00h pixel format mismatch\n", stderr)
        exit(1)
    }
    guard readHEIC, coreImageAvailable else { exit(1) }
}

do {
    try run()
} catch {
    fputs("Probe error: \(error)\n", stderr)
    exit(1)
}
