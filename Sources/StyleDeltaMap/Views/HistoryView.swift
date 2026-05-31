import SwiftUI

struct HistoryView: View {
    @Bindable var store: AppStore

    var body: some View {
        List {
            ForEach(store.history) { record in
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text(record.title)
                            .font(.headline)
                        Spacer()
                        Text(record.date, style: .time)
                            .foregroundStyle(.secondary)
                    }
                    Text(record.command)
                        .font(.system(.caption, design: .monospaced))
                        .foregroundStyle(.secondary)
                        .lineLimit(3)
                        .textSelection(.enabled)
                    if !record.result.standardOutput.isEmpty {
                        Text(record.result.standardOutput)
                            .font(.system(.caption, design: .monospaced))
                            .lineLimit(6)
                            .textSelection(.enabled)
                    }
                    if !record.result.standardError.isEmpty {
                        Text(record.result.standardError)
                            .font(.system(.caption, design: .monospaced))
                            .foregroundStyle(.red)
                            .lineLimit(6)
                            .textSelection(.enabled)
                    }
                }
                .padding(.vertical, 4)
            }
        }
        .overlay {
            if store.history.isEmpty {
                ContentUnavailableView("No Runs Yet", systemImage: "clock", description: Text("Run a workflow to populate history."))
            }
        }
        .navigationTitle("Run History")
    }
}
