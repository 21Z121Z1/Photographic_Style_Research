import SwiftUI
import StyleDeltaMapCore

struct SidebarView: View {
    @Binding var selection: WorkflowKind

    var body: some View {
        List(WorkflowKind.allCases, selection: $selection) { workflow in
            Label {
                VStack(alignment: .leading, spacing: 2) {
                    Text(workflow.title)
                    Text(workflow.subtitle)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                }
            } icon: {
                Image(systemName: workflow.systemImage)
            }
            .tag(workflow)
        }
        .listStyle(.sidebar)
        .navigationTitle("Workflows")
    }
}
