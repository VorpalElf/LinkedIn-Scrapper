import SwiftUI
import MarkdownUI

struct JobRecord: Identifiable, Decodable {
    let id = UUID()
    var job_number: Int?
    var title: String?
    var company: String?
    var location: String?
    var date_posted: String?
    var description: String?
    var company_url: String?
    var company_info: String?           // For enriched company description/info
    var company_num_employees: String?  // For enriched number of employees
}

struct JobResultsView: View {
    let jobs: [JobRecord]
    var body: some View {
        List(jobs) { job in
            VStack(alignment: .leading, spacing: 8) {
                Text(job.title ?? "No Title")
                    .font(.headline)
                Text(job.company ?? "No Company")
                    .font(.subheadline)
                Text(job.location ?? "No Location")
                    .font(.subheadline)
                Text("Posted: \(job.date_posted ?? "N/A")")
                    .font(.caption)
                if let desc = job.description {
                    Markdown(desc)
                        .lineLimit(6)
                }
                if let url = job.company_url {
                    Link("Company Website", destination: URL(string: url)!)
                }
                if let numEmp = job.company_num_employees {
                    Text("Employees: \(numEmp)")
                        .font(.caption)
                }
            }
            .padding(.vertical, 8)
        }
        .navigationTitle("Job Results")
    }
}
