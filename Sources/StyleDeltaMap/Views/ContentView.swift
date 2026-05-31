import SwiftUI

struct ContentView: View {
    @Bindable var store: AppStore

    var body: some View {
        NavigationSplitView {
            SidebarView(selection: $store.selectedWorkflow)
        } detail: {
            DetailContainerView(store: store)
        }
        .navigationSplitViewStyle(.balanced)
        .toolbar {
            ToolbarItemGroup {
                Button {
                    store.runSelectedWorkflow()
                } label: {
                    Label("Run", systemImage: "play.fill")
                }
                .keyboardShortcut(.return, modifiers: [.command])
                .disabled(store.runState.isRunning || store.selectedWorkflow == .history)

                Button {
                    store.clearConsole()
                } label: {
                    Label("Clear Console", systemImage: "eraser")
                }
                .keyboardShortcut("k", modifiers: [.command, .shift])
            }
        }
    }
}

private struct DetailContainerView: View {
    @Bindable var store: AppStore

    var body: some View {
        VStack(spacing: 0) {
            Group {
                switch store.selectedWorkflow {
                case .directInjection:
                    DirectInjectionView(store: store)
                case .reconstruction:
                    ReconstructionView(store: store)
                case .validation:
                    ValidationView(store: store)
                case .history:
                    HistoryView(store: store)
                }
            }
            Divider()
            RunConsoleView(store: store)
                .frame(minHeight: 180, idealHeight: 220, maxHeight: 280)
        }
    }
}
