#!/usr/bin/env swift
import Foundation
import ImageIO

func emit(_ object: [String: Any]) {
    let data = try! JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write(Data("\n".utf8))
}

guard CommandLine.arguments.count == 2 else {
    emit(["ok": false, "error": "usage: swift tools/apple_imageio_validate.swift <image.heic>"])
    exit(64)
}

let path = CommandLine.arguments[1]
let url = URL(fileURLWithPath: path)

guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else {
    emit(["ok": false, "path": path, "stage": "CGImageSourceCreateWithURL", "error": "source is nil"])
    exit(2)
}

let count = CGImageSourceGetCount(source)
guard count > 0 else {
    emit(["ok": false, "path": path, "stage": "CGImageSourceGetCount", "count": count])
    exit(3)
}

guard let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any] else {
    emit(["ok": false, "path": path, "stage": "CGImageSourceCopyPropertiesAtIndex", "count": count])
    exit(4)
}

let width = properties[kCGImagePropertyPixelWidth as String]
let height = properties[kCGImagePropertyPixelHeight as String]
guard width != nil, height != nil else {
    emit([
        "ok": false,
        "path": path,
        "stage": "properties",
        "count": count,
        "pixelWidth": width as Any,
        "pixelHeight": height as Any,
        "propertyKeys": Array(properties.keys).sorted(),
    ])
    exit(5)
}

guard let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
    emit([
        "ok": false,
        "path": path,
        "stage": "CGImageSourceCreateImageAtIndex",
        "count": count,
        "pixelWidth": width as Any,
        "pixelHeight": height as Any,
    ])
    exit(6)
}

emit([
    "ok": true,
    "path": path,
    "count": count,
    "pixelWidth": width as Any,
    "pixelHeight": height as Any,
    "cgImageWidth": image.width,
    "cgImageHeight": image.height,
    "propertyKeys": Array(properties.keys).sorted(),
])
