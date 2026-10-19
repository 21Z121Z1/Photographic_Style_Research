// Native API observations only. No image reconstruction or semantic algorithm.
import Foundation
import ObjectiveC
import CoreImage
import ImageIO
import Metal
import CryptoKit
import Darwin

func sha(_ data: Data) -> String { SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined() }
func progress(_ text: String) { fputs("PROBE_STAGE \(text)\n", stderr); fflush(stderr) }
func writeJSON(_ value: Any, _ url: URL) throws {
    let bytes = try JSONSerialization.data(withJSONObject: value, options: [.prettyPrinted, .sortedKeys, .fragmentsAllowed])
    try (bytes + Data([10])).write(to: url)
    print("TEXTURE_JSON_BEGIN \(url.deletingLastPathComponent().lastPathComponent)/\(url.lastPathComponent)")
    print(String(data: bytes, encoding: .utf8)!)
    print("TEXTURE_JSON_END \(url.deletingLastPathComponent().lastPathComponent)/\(url.lastPathComponent)")
    fflush(stdout)
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
    let rt = method_copyReturnType(method)
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
    if let m = signature(target, name, [], "q") {
        typealias F = @convention(c) (AnyObject, Selector) -> Int64
        return unsafeBitCast(method_getImplementation(m), to: F.self)(target, NSSelectorFromString(name))
    }
    if let m = signature(target, name, [], "f") {
        typealias F = @convention(c) (AnyObject, Selector) -> Float
        return unsafeBitCast(method_getImplementation(m), to: F.self)(target, NSSelectorFromString(name))
    }
    if let m = signature(target, name, [], "d") {
        typealias F = @convention(c) (AnyObject, Selector) -> Double
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
    if let set = value as? Set<String> { return set.sorted() }
    if let dict = value as? [String: Any] { return dict.mapValues { safe($0, depth + 1) } }
    let object = value as AnyObject
    var result: [String: Any] = ["class": String(describing: type(of: object))]
    for key in ["preset", "intensity", "grain", "version", "numberOfPersons", "personInstances", "captureType", "captureMode", "portType", "hardwareModel", "peopleDataVersion", "textureStylePeopleDataVersion", "filmGrainSeed", "persons", "personData", "requiresPersonData", "requiredChannelNames", "optionalChannelNames", "imageMetadata", "dictionaryRepresentation"] {
        if let v = object0(object, key) { result[key] = safe(v, depth + 1) }
        else if let v = scalar0(object, key) { result[key] = v }
    }
    return result
}

let output = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let selectedCase = CommandLine.arguments.count > 3 && CommandLine.arguments[2] == "--case" ? CommandLine.arguments[3] : nil
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
var frameworks: [[String: Any]] = []
for name in ["NeutrinoCore", "PhotoImaging", "CMImaging", "CMCapture"] {
    progress("dlopen \(name)")
    let path = "/System/Library/PrivateFrameworks/\(name).framework/\(name)"
    let handle = dlopen(path, RTLD_NOW | RTLD_LOCAL)
    frameworks.append(["path": path, "loaded": handle != nil, "error": handle != nil ? "" : String(cString: dlerror())])
}
let shouldInventory = selectedCase == nil && !CommandLine.arguments.contains("--requirements") && !CommandLine.arguments.contains("--settings") && !CommandLine.arguments.contains("--processor-preflight") && !CommandLine.arguments.contains("--render-bloom")
if shouldInventory {
progress("copy raw Objective-C class list")
var count: UInt32 = 0
// Filter class names through the public C ABI before bridging matching types.
typealias CopyClasses = @convention(c) (UnsafeMutablePointer<UInt32>) -> UnsafeMutablePointer<UnsafeRawPointer>?
typealias ClassName = @convention(c) (UnsafeRawPointer) -> UnsafePointer<CChar>
let runtimeSymbols = dlopen("/usr/lib/libobjc.A.dylib", RTLD_NOW | RTLD_LOCAL)!
let copyClasses = unsafeBitCast(dlsym(runtimeSymbols, "objc_copyClassList")!, to: CopyClasses.self)
let className = unsafeBitCast(dlsym(runtimeSymbols, "class_getName")!, to: ClassName.self)
let classes = copyClasses(&count)!
var rows: [[String: Any]] = []
for i in 0..<Int(count) {
    let name = String(cString: className(classes[i]))
    if name.contains("TextureStyle") || name == "_NUSemanticStyleProperties" {
        progress("inventory \(name)")
        let cls = unsafeBitCast(classes[i], to: AnyClass.self)
        rows.append(["class": name, "instance_size": class_getInstanceSize(cls),
                     "instance_methods": methodInfo(cls, false), "class_methods": methodInfo(cls, true)])
    }
}
free(classes)
progress("write runtime inventory")
let device = MTLCreateSystemDefaultDevice()
try writeJSON(["schema": "xdremux-texture-runtime-v1", "os": ProcessInfo.processInfo.operatingSystemVersionString,
               "device": device?.name ?? "unavailable", "frameworks": frameworks,
               "classes": rows.sorted { ($0["class"] as! String) < ($1["class"] as! String) },
               "photos_used": false, "patches_to_apple_implementations": false], output.appendingPathComponent("runtime.json"))

var defaults: [String: Any] = [:]
progress("native default dictionaries")
if let pipeline = NSClassFromString("PITextureStylePipelineProcessor") {
    for preset in ["Standard", "Studio", "Soft", "Filmic", "Glowy"] {
        defaults[preset] = safe(object1(pipeline, "defaultTextureStyleDictionaryForPreset:", preset as NSString))
    }
    defaults["inputNames"] = safe(object0(pipeline, "inputNames"))
    defaults["isAvailable"] = scalar0(pipeline, "isAvailable") ?? NSNull()
    defaults["isAvailableForTesting"] = scalar0(pipeline, "isAvailableForTesting") ?? NSNull()
    defaults["testing_override_used"] = false
    for key in ["bloomConfiguration", "diffusionConfiguration", "filmGrainConfiguration", "glowConfiguration", "halationConfiguration"] {
        defaults[key] = safe(object0(pipeline, key))
    }
}
if let processor = NSClassFromString("CMITextureStylesProcessor") { defaults["processorAPIVersion"] = scalar0(processor, "APIVersion") ?? NSNull() }
if let person = NSClassFromString("CMITextureStylesPersonInputData") { defaults["personMetadataFormatVersion"] = scalar0(person, "metadataFormatVersion") ?? NSNull() }
try writeJSON(defaults, output.appendingPathComponent("defaults.json"))
}
if CommandLine.arguments.contains("--inventory") { exit(0) }

if CommandLine.arguments.contains("--settings") {
    var rows: [[String: Any]] = []
    for name in ["FigCaptureTextureStyle", "AVCaptureTextureStyle"] {
        for preset in ["Standard", "Filmic", "Glowy", "Soft", "Studio"] {
            for intensity: Float in [0, 0.5, 1] {
                var row: [String: Any] = ["factory": name, "preset_input": preset, "intensity_input": intensity, "grain_input": Float(0.25), "image_input": false, "capture_metadata_computation": false]
                let selector = "styleWithPreset:intensity:grain:"
                if let cls = NSClassFromString(name), let m = signature(cls, selector, ["@", "f", "f"], "@") {
                    typealias F = @convention(c) (AnyObject, Selector, AnyObject?, Float, Float) -> Unmanaged<AnyObject>?
                    let style = unsafeBitCast(method_getImplementation(m), to: F.self)(cls, NSSelectorFromString(selector), preset as NSString, intensity, 0.25)?.takeUnretainedValue()
                    row["native_style"] = safe(style)
                } else { row["unsupported"] = true }
                rows.append(row)
            }
        }
    }
    try writeJSON(rows, output.appendingPathComponent("settings.json")); exit(0)
}

if CommandLine.arguments.contains("--processor-preflight") {
    var result: [String: Any] = ["scope": "default native processor initialization/prewarm only, no image or person context supplied", "input_images_supplied": false, "apple_implementation_patched": false]
    if let cls = NSClassFromString("CMITextureStylesProcessor") {
        result["APIVersion"] = scalar0(cls, "APIVersion") ?? NSNull()
        progress("native processor init")
        var processor: AnyObject?
        if CommandLine.arguments.contains("--queue-nil") || CommandLine.arguments.contains("--queue-metal") {
            let device = MTLCreateSystemDefaultDevice()
            let queue: AnyObject? = CommandLine.arguments.contains("--queue-metal") ? device?.makeCommandQueue() : nil
            result["system_metal_device"] = device?.name ?? "unavailable"
            result["system_queue_supplied"] = queue != nil
            if let allocation = object0(cls, "alloc") {
                result["allocation_non_nil"] = true
                progress("native processor initWithOptionalMetalCommandQueue")
                processor = object1(allocation, "initWithOptionalMetalCommandQueue:", queue)
            }
        } else { processor = object0(cls, "new") }
        if let processor {
            result["initialized"] = true
            for selector in ["setup", "prewarm"] {
                guard let m = signature(processor, selector, [], "i") else { result[selector] = "unsupported-ABI"; continue }
                typealias F = @convention(c) (AnyObject, Selector) -> Int32
                progress("native processor \(selector)")
                let status = unsafeBitCast(method_getImplementation(m), to: F.self)(processor, NSSelectorFromString(selector))
                result[selector] = status
                if status != 0 { break }
            }
            result["supportsExternalMemoryResource"] = scalar0(processor, "supportsExternalMemoryResource") ?? NSNull()
        } else { result["initialized"] = false }
    } else { result["unsupported"] = "CMITextureStylesProcessor class unavailable" }
    try writeJSON(result, output.appendingPathComponent("processor-preflight.json")); exit(0)
}

if let index = CommandLine.arguments.firstIndex(of: "--requirements"), index + 1 < CommandLine.arguments.count {
    let effect = UInt64(CommandLine.arguments[index + 1])!
    let selector = "inputConfigurationForEffectType:isVideo:"
    var result: [String: Any] = ["effect_type": effect, "is_video": false, "selector": selector]
    if let cls = NSClassFromString("PITextureStylePipelineProcessor"), let m = signature(cls, selector, ["Q", "B"], "@") {
        typealias F = @convention(c) (AnyObject, Selector, UInt64, Bool) -> Unmanaged<AnyObject>?
        progress("native effect requirements \(effect)")
        let configuration = unsafeBitCast(method_getImplementation(m), to: F.self)(cls, NSSelectorFromString(selector), effect, false)?.takeUnretainedValue()
        result["configuration"] = safe(configuration)
    } else { result["unsupported"] = true }
    try writeJSON(result, output.appendingPathComponent("requirements.json")); exit(0)
}

var cases: [[String: Any]] = []
let base: [String: Any] = ["Preset": "Standard", "CaptureType": "LF", "CaptureMode": "Still", "PortType": "PortTypeBack", "HardwareModel": "iPhone19,2", "TextureStylePeopleDataVersion": 3, "FilmGrainSeed": 0]
var studio = base; studio["Preset"] = "Studio"
var missingHardware = base; missingHardware.removeValue(forKey: "HardwareModel")
var badVersion = base; badVersion["TextureStylePeopleDataVersion"] = 999

if let index = CommandLine.arguments.firstIndex(of: "--render-bloom"), index + 2 < CommandLine.arguments.count {
    let manifestURL = URL(fileURLWithPath: CommandLine.arguments[index + 1])
    let intensity = Double(CommandLine.arguments[index + 2])!
    var report: [String: Any] = ["scope": "controlled native Bloom CI kernel only; no full Texture producer, no original capture or Photos activation", "intensity": intensity, "input_domain": "analytical extended linear Display P3", "linear_thumbnail_resource_created": false, "semantic_roles_synthesized": false, "apple_implementation_patched": false]
    func checkpoint() throws { try writeJSON(report, output.appendingPathComponent("render-bloom.json")) }
    do {
        guard let pipeline = NSClassFromString("PITextureStylePipelineProcessor"), scalar0(pipeline, "isAvailable") as? Bool == true else { throw NSError(domain: "ProbeAvailability", code: 77) }
        let config = object0(pipeline, "bloomConfiguration")
        report["native_bloom_input_configuration"] = safe(config)
        // Bloom reports no required/optional semantic channels or thumbnail.
        // Use one image only; no fake auxiliary resource occupies another role.
        guard let kernel = NSClassFromString("PITextureStyleProcessorKernel") as? CIImageProcessorKernel.Type else { throw NSError(domain: "ProbeKernelType", code: 77) }
        var metadata = base; metadata["Preset"] = "Glowy"
        let data = try PropertyListSerialization.data(fromPropertyList: metadata, format: .binary, options: 0)
        let selector = "textureStylePropertiesFromImageMetadata:auxImageMetadata:error:"
        guard let propsClass = NSClassFromString("_NUTextureStyleProperties"), let m = signature(propsClass, selector, ["@", "@", "o^@"], "@") else { throw NSError(domain: "ProbeMetadataABI", code: 77) }
        typealias Parse = @convention(c) (AnyObject, Selector, AnyObject?, AnyObject?, UnsafeMutablePointer<NSError?>) -> Unmanaged<AnyObject>?
        var error: NSError?
        guard let properties = unsafeBitCast(method_getImplementation(m), to: Parse.self)(propsClass, NSSelectorFromString(selector), data as NSData, NSDictionary(), &error)?.takeUnretainedValue() else { throw error ?? NSError(domain: "ProbeMetadata", code: 1) }
        guard let tuningClass = NSClassFromString("CMITextureStyleTuningLookup"), let tuning = object1(tuningClass, "tuningDictionaryForMetadata:", metadata as NSDictionary) as? NSDictionary else { throw NSError(domain: "ProbeNativeTuning", code: 1) }
        let common = tuning["Common"] as? NSDictionary ?? tuning
        report["tuning_target"] = metadata
        report["tuning_target_is_original_camera_claim"] = false
        report["native_tuning_keys"] = common.allKeys.map { String(describing: $0) }.sorted()
        report["native_bloom_tuning"] = safe(common["Bloom"])
        let descriptorSelector = "descriptorForEffectName:tuningDictionary:semanticStyleProperties:semanticStyleInfo:"
        guard let descriptorMethod = signature(kernel, descriptorSelector, ["@", "@", "@", "@"], "@") else { throw NSError(domain: "ProbeDescriptorABI", code: 77) }
        typealias Descriptor = @convention(c) (AnyObject, Selector, AnyObject?, AnyObject?, AnyObject?, AnyObject?) -> Unmanaged<AnyObject>?
        guard let descriptor = unsafeBitCast(method_getImplementation(descriptorMethod), to: Descriptor.self)(kernel, NSSelectorFromString(descriptorSelector), "Bloom" as NSString, common, nil, NSDictionary())?.takeUnretainedValue() else { throw NSError(domain: "ProbeDescriptor", code: 1) }
        report["descriptor"] = safe(descriptor)
        let manifest = try JSONSerialization.jsonObject(with: Data(contentsOf: manifestURL)) as! [String: Any]
        let entry = (manifest["inputs"] as! [[String: Any]]).first { $0["name"] as? String == "landscape-hdr-edge" }!
        let raw = try Data(contentsOf: manifestURL.deletingLastPathComponent().appendingPathComponent(entry["file"] as! String))
        guard sha(raw) == entry["sha256"] as? String else { throw NSError(domain: "ProbeInputHash", code: 1) }
        let width = entry["width"] as! Int, height = entry["height"] as! Int
        let rect = CGRect(x: 0, y: 0, width: CGFloat(width), height: CGFloat(height))
        let color = CGColorSpace(name: CGColorSpace.extendedLinearDisplayP3)!
        let image = CIImage(bitmapData: raw, bytesPerRow: width*16, size: rect.size, format: .RGBAf, colorSpace: color)
        guard let device = MTLCreateSystemDefaultDevice() else { throw NSError(domain: "ProbeMetal", code: 77) }
        let context = CIContext(mtlDevice: device, options: [.workingColorSpace: color, .workingFormat: CIFormat.RGBAh.rawValue])
        report["metal_device"] = device.name
        report["source_sha256"] = sha(raw)
        report["input_count"] = 1
        report["before_apply"] = true
        try checkpoint()
        let arguments: [String: Any] = ["usage": 1, "intensity": intensity, "grainIntensity": 0, "textureStyleProperties": properties, "isVideo": false, "effectDescriptors": [descriptor], "extents": [CIVector(cgRect: rect)]]
        progress("native Bloom apply intensity=\(intensity)")
        let result: CIImage? = try kernel.apply(withExtent: rect, inputs: [image], arguments: arguments)
        guard let result else { throw NSError(domain: "ProbeNativeApplyNil", code: 1) }
        report["apply_returned_image"] = true
        try checkpoint()
        var original = Data(count: width*height*16), rendered = original
        original.withUnsafeMutableBytes { b in context.render(image, toBitmap: b.baseAddress!, rowBytes: width*16, bounds: rect, format: .RGBAf, colorSpace: color) }
        progress("native Bloom render intensity=\(intensity)")
        rendered.withUnsafeMutableBytes { b in context.render(result, toBitmap: b.baseAddress!, rowBytes: width*16, bounds: rect, format: .RGBAf, colorSpace: color) }
        try original.write(to: output.appendingPathComponent("baseline.rgba32f"))
        try rendered.write(to: output.appendingPathComponent("rendered.rgba32f"))
        report["baseline_native_sha256"] = sha(original)
        report["rendered_native_sha256"] = sha(rendered)
        report["rendered_differs_from_baseline"] = original != rendered
        report["render_completed"] = true
    } catch { report["native_or_contract_error"] = String(describing: error); report["render_completed"] = false }
    try checkpoint(); exit(0)
}

for (name, dictionary) in [("synthetic-standard-control", base), ("synthetic-studio-control", studio), ("missing-hardware", missingHardware), ("unsupported-version", badVersion), ("empty-dictionary", [:])] {
    if let selectedCase, name != selectedCase { continue }
    let data = try PropertyListSerialization.data(fromPropertyList: dictionary, format: .binary, options: 0)
    var row: [String: Any] = ["case": name, "input": dictionary, "input_sha256": sha(data), "scope": "metadata-only diagnostic, never camera provenance or Photos admission"]
    let selector = "textureStylePropertiesFromImageMetadata:auxImageMetadata:error:"
    progress("metadata consumer \(name)")
    let consumerClass = NSClassFromString("_NUTextureStyleProperties")
    row["consumer_class_available"] = consumerClass != nil
    if let cls = consumerClass, let method = class_getClassMethod(cls, NSSelectorFromString(selector)) {
        row["consumer_encoding"] = String(cString: method_getTypeEncoding(method)!)
    }
    if let cls = consumerClass, let m = signature(cls, selector, ["@", "@", "o^@"], "@") {
        typealias F = @convention(c) (AnyObject, Selector, AnyObject?, AnyObject?, UnsafeMutablePointer<NSError?>) -> Unmanaged<AnyObject>?
        var error: NSError?
        let properties = unsafeBitCast(method_getImplementation(m), to: F.self)(cls, NSSelectorFromString(selector), data as NSData, NSDictionary(), &error)?.takeUnretainedValue()
        row["native_consumer_called"] = true
        row["native_returned_object"] = properties != nil
        row["properties"] = safe(properties)
        row["error"] = error.map { ["domain": $0.domain, "code": $0.code, "description": $0.localizedDescription] as [String: Any] } ?? [:]
        if let properties, let kernel = NSClassFromString("PITextureStyleProcessorKernel") {
            row["person_input_data"] = safe(object1(kernel, "personInputDataFromStillProperties:", properties))
        }
    } else { row["unsupported"] = selector; row["unsupported_reason"] = consumerClass == nil ? "class_unavailable" : "selector_or_ABI_mismatch" }
    cases.append(row)
    try writeJSON(cases, output.appendingPathComponent("metadata-cases.json"))
}
print("NATIVE_METADATA_PROBE_RECORDED cases=\(cases.count); full_image_activation=false")
