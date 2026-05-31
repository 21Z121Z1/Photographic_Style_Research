// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "StyleDeltaMap",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "StyleDeltaMap", targets: ["StyleDeltaMap"])
    ],
    targets: [
        .target(
            name: "StyleDeltaMapCore",
            path: "Sources/StyleDeltaMapCore"
        ),
        .executableTarget(
            name: "StyleDeltaMap",
            dependencies: ["StyleDeltaMapCore"],
            path: "Sources/StyleDeltaMap"
        ),
        .testTarget(
            name: "StyleDeltaMapTests",
            dependencies: ["StyleDeltaMapCore"],
            path: "tests/StyleDeltaMapTests"
        )
    ]
)
