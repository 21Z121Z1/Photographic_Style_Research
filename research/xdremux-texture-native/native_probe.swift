// Native API observations only. No image reconstruction or semantic algorithm.
import Foundation
import ObjectiveC
import CoreImage
import ImageIO
import Metal
import CryptoKit
import Darwin

func sha(_ data: Data) -> String { SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined() }
func writeJSON(_ value: Any, _ url: URL) throws {
    let bytes = try JSONSerialization.data(withJSONObject: value, options: [.prettyPrinted, .sortedKeys, .fragmentsAllowed])
    try (bytes + Data([10])).write(to: url)
}
func methodInfo(_ cls: AnyClass, _ meta: Bool) -> [[String: Any]] {
    var count: UInt32 = 0
    guard let list = class_copyMethodList(meta ? object_getClass(cls) : cls, &count) else { return [] }
    defer { free(list) }
    return (0..<Int(count)).map { i in
        ["selector": NSStringFromSelector(method_getName(list[i])),
         "encoding": String(cString: method_getTypeEncoding(list[i])!)]
    }.sorted { ($0["selector"] as! String) < ($1["selector"] as! String) }
}
func signature(_ target: AnyObject, _ name: String, _ args: [String], _ ret: String) -> Method? {
    let sel = NSSelectorFromString(name)
    guard let cls = object_getClass(target), let method = class_getInstanceMethod(cls, sel),
          method_getNumberOfArguments(method) == UInt32(args.count + 2) else { return nil }
    guard let rt = method_copyReturnType(method) else { return nil }
    defer { free(rt) }
    guard String(cString: rt) == ret else { return nil }
    for (i, expected) in args.enumerated() {
        guard let at = method_copyArgumentType(method, UInt32(i + 2)) else { return nil }
        let actual = String(cString: at); free(at)
        if actual != expected { return nil }
    }
    return method
}
func object0(_ target: AnyObject, _ name: String) -> AnyObject? {
    guard let m = signature(target, name, [], "@") else { return nil }
    typealias F = @convention(c) (AnyObject, Selector) -> Unmanaged<AnyObject>?
    return unsafeBitCast(method_getImplementation(m), to: F.self)(target, NSSelectorFromString(name))?.takeUnretainedValue()
}
func object1(_ target: AnyObject, _ name: String, _ value: AnyObject?) -> AnyObject? {
    guard let m = signature(target, name, ["@"], "@") else { return nil }
    typealias F = @convention(c) (AnyObject, Selector, AnyObject?) -> Unmanaged<AnyObject>?
    return unsafeBitCast(method_getImplementation(m), to: F.self)(target, NSSelectorFromString(name), value)?.takeUnretainedValue()
}
func scalar0(_ target: AnyObject, _ name: String) -> Any? {
    if let m = signature(target, name, [], "B") {
        typealias F = @convention(c) (AnyObject, Selector) -> Bool
        return unsafeBitCast(method_getImplementation(m), to: F.self)(target, NSSelectorFromString(name))
    }
    if let m = signature(target, name, [], "Q") {
        typealias F = @convention(c) (AnyObject, Selector) -> UInt64
        return unsafeBitCast(method_getImplementation(m), to: F.self)(target, NSSelectorFromString(name))
    }
    return nil
}
func safe(_ value: Any?, _ depth: Int = 0) -> Any {
    guard let value else { return NSNull() }
    if depth > 5 { return "depth-limit" }
    if let data = value as? Data { return ["bytes": data.count, "sha256": sha(data)] as [String: Any] }
    if let value = value as? String { return value }
    if let value = value as? NSNumber { return value }
    if let array = value as? [Any] { return array.map { safe($0, depth + 1) } }
    if let dict = value as? [String: Any] { return dict.mapValues { safe($0, depth + 1) } }
    let object = value as AnyObject
    var result: [String: Any] = ["class": String(describing: type(of: object))]
    for key in ["preset", "captureType", "captureMode", "portType", "hardwareModel", "peopleDataVersion", "textureStylePeopleDataVersion", "filmGrainSeed", "persons", "personData", "requiresPersonData", "requiresLinearThumbnail", "imageMetadata", "dictionaryRepresentation"] {
        if let v = object0(object, key) { result[key] = safe(v, depth + 1) }
        else if let v = scalar0(object, key) { result[key] = v }
    }
    return result
}

let output = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
var frameworks: [[String: Any]] = []
for name in ["NeutrinoCore", "PhotoImaging", "CMImaging", "CMCapture"] {
    let path = "/System/Library/PrivateFrameworks/\(name).framework/\(name)"
    let handle = dlopen(path, RTLD_NOW | RTLD_LOCAL)
    frameworks.append(["path": path, "loaded": handle != nil, "error": handle != nil ? "" : String(cString: dlerror())])
}
var count: UInt32 = 0
let classes = objc_copyClassList(&count)!
var rows: [[String: Any]] = []
for i in 0..<Int(count) {
    let cls = classes[i], name = NSStringFromClass(cls)
    if name.contains("TextureStyle") || name == "_NUSemanticStyleProperties" {
        rows.append(["class": name, "instance_size": class_getInstanceSize(cls),
                     "instance_methods": methodInfo(cls, false), "class_methods": methodInfo(cls, true)])
    }
}
free(classes)
let device = MTLCreateSystemDefaultDevice()
try writeJSON(["schema": "xdremux-texture-runtime-v1", "os": ProcessInfo.processInfo.operatingSystemVersionString,
               "device": device?.name ?? "unavailable", "frameworks": frameworks,
               "classes": rows.sorted { ($0["class"] as! String) < ($1["class"] as! String) },
               "photos_used": false, "patches_to_apple_implementations": false], output.appendingPathComponent("runtime.json"))

var defaults: [String: Any] = [:]
if let pipeline = NSClassFromString("PITextureStylePipelineProcessor") {
    for preset in ["Standard", "Studio", "Soft", "Filmic", "Glowy"] {
        defaults[preset] = safe(object1(pipeline, "defaultTextureStyleDictionaryForPreset:", preset as NSString))
    }
    defaults["inputNames"] = safe(object0(pipeline, "inputNames"))
}
try writeJSON(defaults, output.appendingPathComponent("defaults.json"))

var cases: [[String: Any]] = []
let base: [String: Any] = ["Preset": "Standard", "CaptureType": "LF", "CaptureMode": "Still", "PortType": "PortTypeBack", "HardwareModel": "iPhone19,2", "TextureStylePeopleDataVersion": 3, "FilmGrainSeed": 0]
var studio = base; studio["Preset"] = "Studio"
var missingHardware = base; missingHardware.removeValue(forKey: "HardwareModel")
var badVersion = base; badVersion["TextureStylePeopleDataVersion"] = 999
for (name, dictionary) in [("synthetic-standard-control", base), ("synthetic-studio-control", studio), ("missing-hardware", missingHardware), ("unsupported-version", badVersion), ("empty-dictionary", [:])] {
    let data = try PropertyListSerialization.data(fromPropertyList: dictionary, format: .binary, options: 0)
    var row: [String: Any] = ["case": name, "input": dictionary, "input_sha256": sha(data), "scope": "metadata-only diagnostic, never camera provenance or Photos admission"]
    let selector = "textureStylePropertiesFromImageMetadata:auxImageMetadata:error:"
    if let cls = NSClassFromString("_NUTextureStyleProperties"), let m = signature(cls, selector, ["@", "@", "^@"], "@") {
        typealias F = @convention(c) (AnyObject, Selector, AnyObject?, AnyObject?, UnsafeMutablePointer<NSError?>) -> Unmanaged<AnyObject>?
        var error: NSError?
        let properties = unsafeBitCast(method_getImplementation(m), to: F.self)(cls, NSSelectorFromString(selector), data as NSData, NSDictionary(), &error)?.takeUnretainedValue()
        row["native_returned_object"] = properties != nil
        row["properties"] = safe(properties)
        row["error"] = error.map { ["domain": $0.domain, "code": $0.code, "description": $0.localizedDescription] as [String: Any] } ?? [:]
        if let properties, let kernel = NSClassFromString("PITextureStyleProcessorKernel") {
            row["person_input_data"] = safe(object1(kernel, "personInputDataFromStillProperties:", properties))
        }
    } else { row["unsupported"] = selector }
    cases.append(row)
    try writeJSON(cases, output.appendingPathComponent("metadata-cases.json"))
}
print("NATIVE_METADATA_PROBE_RECORDED cases=\(cases.count); full_image_activation=false")
