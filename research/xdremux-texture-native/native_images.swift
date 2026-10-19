// Only Apple codec, color-management and consumer APIs. Charts are authored in Rust.
import Foundation
import CoreImage
import ImageIO
import UniformTypeIdentifiers
import CryptoKit

func sha(_ data: Data) -> String { SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined() }
func save(_ object: Any, _ url: URL) throws {
    let data = try JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
    try (data + Data([10])).write(to: url)
    print("TEXTURE_JSON_BEGIN \(url.lastPathComponent)")
    print(String(data: data, encoding: .utf8)!)
    print("TEXTURE_JSON_END \(url.lastPathComponent)")
}
let linear = CGColorSpace(name: CGColorSpace.extendedLinearDisplayP3)!
let p3 = CGColorSpace(name: CGColorSpace.displayP3)!
let context = CIContext(options: [.workingColorSpace: linear, .workingFormat: CIFormat.RGBAh.rawValue])

func facts(_ url: URL) -> [String: Any] {
    var f: [String: Any] = ["file": url.lastPathComponent, "original_camera_information": false,
        "original_raw": false, "texture_activation": "unverified"]
    guard let data = try? Data(contentsOf: url), let src = CGImageSourceCreateWithData(data as CFData, nil) else {
        f["imageio_source"] = false; return f
    }
    f["file_sha256"] = sha(data); f["size"] = data.count
    f["type"] = CGImageSourceGetType(src).map { $0 as String } ?? "unknown"
    let properties = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) as? [String: Any] ?? [:]
    for key in [kCGImagePropertyPixelWidth, kCGImagePropertyPixelHeight, kCGImagePropertyOrientation, kCGImagePropertyDepth, kCGImagePropertyColorModel, kCGImagePropertyProfileName] {
        f[key as String] = properties[key as String] ?? NSNull()
    }
    f["iso_gain_map"] = CGImageSourceCopyAuxiliaryDataInfoAtIndex(src, 0, kCGImageAuxiliaryDataTypeISOGainMap) != nil
    f["apple_gain_map"] = CGImageSourceCopyAuxiliaryDataInfoAtIndex(src, 0, kCGImageAuxiliaryDataTypeHDRGainMap) != nil
    if let cg = CGImageSourceCreateImageAtIndex(src, 0, nil) {
        f["imageio_decoded"] = true; f["decoded_bits_per_component"] = cg.bitsPerComponent
        f["decoded_color_space"] = cg.colorSpace?.name.map { $0 as String } ?? "unknown"
    } else { f["imageio_decoded"] = false }
    if let ci = CIImage(contentsOf: url, options: [.applyOrientationProperty: false, .expandToHDR: true]) {
        f["coded_extent"] = [ci.extent.width, ci.extent.height]
        if #available(macOS 15, *) { f["content_headroom"] = ci.contentHeadroom }
        let w = Int(ci.extent.width), h = Int(ci.extent.height)
        if w > 0 && h > 0 && w * h <= 1_000_000 {
            var rgba = Data(count: w*h*16)
            rgba.withUnsafeMutableBytes { bytes in
                context.render(ci, toBitmap: bytes.baseAddress!, rowBytes: w*16, bounds: ci.extent, format: .RGBAf, colorSpace: linear)
            }
            f["native_decoded_linear_p3_rgba32f_sha256"] = sha(rgba)
        }
    }
    return f
}
if CommandLine.arguments[1] == "--inspect" {
    let input = URL(fileURLWithPath: CommandLine.arguments[2])
    try save(facts(input), URL(fileURLWithPath: CommandLine.arguments[3])); exit(0)
}
let manifestURL = URL(fileURLWithPath: CommandLine.arguments[1])
let destination = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
try FileManager.default.createDirectory(at: destination, withIntermediateDirectories: true)
let manifest = try JSONSerialization.jsonObject(with: Data(contentsOf: manifestURL)) as! [String: Any]
precondition(manifest["original_camera_information"] as? Bool == false)
var reports: [[String: Any]] = []
for entry in manifest["inputs"] as! [[String: Any]] {
    let name = entry["name"] as! String
    let width = entry["width"] as! Int, height = entry["height"] as! Int
    let orientation = entry["orientation"] as! Int
    func image(_ key: String, _ hash: String) throws -> CIImage {
        let filename = entry[key] as! String
        precondition(!filename.contains("/"))
        let raw = try Data(contentsOf: manifestURL.deletingLastPathComponent().appendingPathComponent(filename))
        precondition(raw.count == width*height*16 && sha(raw) == entry[hash] as! String)
        return CIImage(bitmapData: raw, bytesPerRow: width*16, size: CGSize(width: CGFloat(width), height: CGFloat(height)), format: .RGBAf, colorSpace: linear)
    }
    let hdr = try image("file", "sha256"), sdr = try image("sdr_file", "sdr_sha256")
    let rect = CGRect(x: 0, y: 0, width: CGFloat(width), height: CGFloat(height))
    guard let cg = context.createCGImage(sdr, from: rect, format: .RGBA8, colorSpace: p3) else { fatalError("synthetic CGImage unavailable") }
    for (ext, type) in [("jpg", UTType.jpeg.identifier), ("heic", UTType.heic.identifier)] {
        let url = destination.appendingPathComponent(name+"-sdr."+ext)
        var row: [String: Any] = ["case": name+"-sdr-"+ext, "requested_orientation": orientation, "input_raw_sha256": entry["sdr_sha256"]!]
        if let out = CGImageDestinationCreateWithURL(url as CFURL, type as CFString, 1, nil) {
            CGImageDestinationAddImage(out, cg, [kCGImagePropertyOrientation as String: orientation, kCGImageDestinationLossyCompressionQuality as String: 0.9] as CFDictionary)
            row["write_succeeded"] = CGImageDestinationFinalize(out)
            row["facts"] = facts(url)
        } else { row["unsupported"] = "ImageIO destination unavailable: "+type }
        reports.append(row)
    }
    if entry["hdr"] as! Bool {
        let url = destination.appendingPathComponent(name+"-pq.heic")
        var row: [String: Any] = ["case": name+"-pq", "input_raw_sha256": entry["sha256"]!, "requested_orientation": 1]
        do {
            let pq = CGColorSpace(name: CGColorSpace.itur_2100_PQ)!
            try context.writeHEIF10Representation(of: hdr, to: url, colorSpace: pq, options: [:])
            row["facts"] = facts(url); row["write_succeeded"] = true
        } catch { row["native_error"] = String(describing: error); row["write_succeeded"] = false }
        reports.append(row)
        let adaptiveURL = destination.appendingPathComponent(name+"-adaptive.heic")
        var adaptive: [String: Any] = ["case": name+"-adaptive", "input_raw_sha256": entry["sha256"]!, "requested_orientation": 1]
        do {
            try context.writeHEIFRepresentation(of: sdr, to: adaptiveURL, format: .RGBA8, colorSpace: p3, options: [.hdrImage: hdr])
            adaptive["facts"] = facts(adaptiveURL); adaptive["write_succeeded"] = true
        } catch { adaptive["native_error"] = String(describing: error); adaptive["write_succeeded"] = false }
        reports.append(adaptive)
    }
    try save(["schema": "xdremux-native-synthetic-matrix-v1", "os": ProcessInfo.processInfo.operatingSystemVersionString, "license": "CC0-1.0", "no_photos_read": true, "rows": reports], destination.appendingPathComponent("image-matrix.json"))
}
print("NATIVE_SYNTHETIC_IMAGE_MATRIX_RECORDED rows=\(reports.count)")
