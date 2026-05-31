import AppKit
import SwiftUI

final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        NSApp.activate(ignoringOtherApps: true)
    }
}

@main
struct StyleDeltaMapApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @State private var store = AppStore()

    var body: some Scene {
        WindowGroup("StyleDeltaMap") {
            ContentView(store: store)
                .frame(minWidth: 1040, minHeight: 680)
        }
        .commands {
            CommandGroup(after: .newItem) {
                Button("Run Selected Workflow") {
                    store.runSelectedWorkflow()
                }
                .keyboardShortcut(.return, modifiers: [.command])
                .disabled(store.runState.isRunning || store.selectedWorkflow == .history)

                Button("Clear Console") {
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
