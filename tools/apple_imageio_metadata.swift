import Foundation
import ImageIO

func jsonValue(_ value: Any, depth: Int = 0) -> Any {
    if depth > 6 {
        return String(describing: value)
    }
    if let data = value as? Data {
        return ["type": "data", "bytes": data.count]
    }
    if let number = value as? NSNumber {
        return number
    }
    if let string = value as? String {
        return string
    }
    if let array = value as? [Any] {
        return array.map { jsonValue($0, depth: depth + 1) }
    }
    if let dict = value as? [AnyHashable: Any] {
        var result: [String: Any] = [:]
        for key in dict.keys {
            result[String(describing: key)] = jsonValue(dict[key]!, depth: depth + 1)
        }
        return result
    }
    return String(describing: value)
}

func sortedKeys(_ value: Any?) -> [String] {
    guard let dict = value as? [AnyHashable: Any] else {
        return []
    }
    return dict.keys.map { String(describing: $0) }.sorted()
}

var rows: [[String: Any]] = []
for path in CommandLine.arguments.dropFirst() {
    let url = URL(fileURLWithPath: path)
    var row: [String: Any] = ["path": path]
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else {
        row["error"] = "CGImageSourceCreateWithURL failed"
        rows.append(row)
        continue
    }
    row["image_count"] = CGImageSourceGetCount(source)
    guard let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any] else {
        row["error"] = "CGImageSourceCopyPropertiesAtIndex failed"
        rows.append(row)
        continue
    }
    let makerAppleKey = kCGImagePropertyMakerAppleDictionary as String
    let makerApple = props[makerAppleKey] ?? props["{MakerApple}"]
    row["has_maker_apple"] = makerApple != nil
    row["maker_apple_keys"] = sortedKeys(makerApple)
    row["maker_apple"] = makerApple.map { jsonValue($0) } ?? NSNull()
    row["has_exif_dictionary"] = props[kCGImagePropertyExifDictionary as String] != nil
    row["has_tiff_dictionary"] = props[kCGImagePropertyTIFFDictionary as String] != nil
    row["top_level_keys"] = props.keys.sorted()
    rows.append(row)
}

let output = try JSONSerialization.data(withJSONObject: rows, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(output)
FileHandle.standardOutput.write(Data("\n".utf8))
