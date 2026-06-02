import AppKit
import SwiftUI

final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationWillFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.activate()
    }
}

@main
struct StyleDeltaMapApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @State private var store = AppStore()

    var body: some Scene {
        WindowGroup(String(localized: "StyleDeltaMap", comment: "App window title")) {
            ContentView(store: store)
                .frame(minWidth: 1040, minHeight: 680)
        }
        .commands {
            CommandGroup(after: .newItem) {
                Button(String(localized: "Run Selected Workflow", comment: "Menu command")) {
                    store.runSelectedWorkflow()
                }
                .keyboardShortcut(.return, modifiers: [.command])
                .disabled(store.runState.isRunning || store.selectedWorkflow == .history)

                Button(String(localized: "Clear Console", comment: "Menu command")) {
                    store.clearConsole()
                }
                .keyboardShortcut("k", modifiers: [.command, .shift])
            }
        }

        Settings {
            SettingsView(store: store)
        }
    }
}
