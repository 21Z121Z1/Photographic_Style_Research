import SwiftUI

struct RunConsoleView: View {
    @Bindable var store: AppStore

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack {
                Text("Console")
                    .font(.headline)
                Spacer()
                Text(store.runState.label)
                    .font(.caption)
                    .foregroundStyle(statusColor)
            }
            .padding(.horizontal)
            .padding(.vertical, 8)

            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 8) {
                        ForEach(store.messages) { message in
                            Text(message.text)
                                .font(.system(.caption, design: .monospaced))
                                .textSelection(.enabled)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .id(message.id)
                        }
                    }
                    .padding(.horizontal)
                    .padding(.bottom)
                }
                .onChange(of: store.messages.count) { _, _ in
                    if let last = store.messages.last {
                        proxy.scrollTo(last.id, anchor: .bottom)
                    }
                }
            }
        }
    }

    private var statusColor: Color {
        switch store.runState {
        case .idle:
            .secondary
        case .running:
            .accentColor
        case .succeeded:
            .green
        case .failed:
            .red
        }
    }
}
