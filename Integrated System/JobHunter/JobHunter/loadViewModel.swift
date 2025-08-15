//
//  loadViewModel.swift
//  JobHunter
//
//  Created by Jeremy Lo on 14/8/25.
//

import Foundation

class loadViewModel: ObservableObject {

	@Published var jobs: [JobRecord] = []
	@Published var isLoading: Bool = false
	@Published var errorMessage: String? = nil
	@Published var statusMessage: String = ""
	@Published var enrichmentComplete: Bool = false

	func fetchJobs(searchTerm: String, location: String, numResults: Int, sitesPicked: [String], fullDescription: Bool, completion: @escaping (Bool) -> Void) {
		isLoading = true
		enrichmentComplete = false
		errorMessage = nil
		statusMessage = "Fetching jobs..."
		guard let url = URL(string: "http://192.168.1.143:5000/JobSpy") else {
			errorMessage = "Invalid backend URL"
			isLoading = false
			completion(false)
			return
		}
		var request = URLRequest(url: url)
		request.httpMethod = "POST"
		request.timeoutInterval = 600
		request.setValue("application/json", forHTTPHeaderField: "Content-Type")
		let body: [String: Any] = [
			"site_name": sitesPicked.map { $0.lowercased() },
			"search_term": searchTerm,
			"location": location,
			"results_wanted": numResults,
			"fetch_description": fullDescription,
			"rotate_proxies": true
		]
		request.httpBody = try? JSONSerialization.data(withJSONObject: body)

		URLSession.shared.dataTask(with: request) { data, response, error in
			DispatchQueue.main.async {
				if let error = error {
					self.errorMessage = error.localizedDescription
					print("JobSpy query error:", error)
					self.isLoading = false
					completion(false)
					return
				}
				self.statusMessage = "Consolidating..."
				self.runGoogleSearch {
                    self.runApollo {
                        self.fetchJobResults { success in
                            self.enrichmentComplete = success
                            completion(success)
                        }
                    }
                }
			}
		}.resume()
	}

	func fetchJobResults(completion: @escaping (Bool) -> Void) {
		guard let url = URL(string: "http://192.168.1.143:5000/jobs") else {
			errorMessage = "Invalid jobs URL"
			isLoading = false
			completion(false)
			return
		}
		URLSession.shared.dataTask(with: url) { data, response, error in
			DispatchQueue.main.async {
				self.isLoading = false
				if let error = error {
					self.errorMessage = error.localizedDescription
					print("fetchJobResults error:", error)
					completion(false)
					print(error)
					return
				}
				guard let data = data, !data.isEmpty else {
					self.errorMessage = "No data received or data is empty"
					completion(false)
					return
				}
				// Check if data is valid JSON before decoding
				do {
					// Try to decode as JSON array
					let jobs = try JSONDecoder().decode([JobRecord].self, from: data)
					self.jobs = jobs
					completion(true)
				} catch {
					// Try to decode as error JSON
					if let errorJson = try? JSONSerialization.jsonObject(with: data) as? [String: Any], let errorMsg = errorJson["error"] as? String {
						self.errorMessage = "Backend error: \(errorMsg)"
						print("Backend error:", errorMsg)
					} else {
						self.errorMessage = "Failed to decode jobs: \(error)"
						print(error)
					}
					completion(false)
				}
			}
		}.resume()
	}

	// GoogleSearch enrichment step
	func runGoogleSearch(completion: @escaping () -> Void) {
		self.statusMessage = "Enriching with GoogleSearch..."
		guard let url = URL(string: "http://192.168.1.143:5000/enrich_googlesearch") else { completion(); return }
		var request = URLRequest(url: url)
		request.httpMethod = "POST"
		request.timeoutInterval = 600
		request.setValue("application/json", forHTTPHeaderField: "Content-Type")
		request.httpBody = try? JSONSerialization.data(withJSONObject: [:])

		URLSession.shared.dataTask(with: request) { data, response, error in
			DispatchQueue.main.async {
				if let error = error {
					self.statusMessage = "GoogleSearch enrichment failed."
					print("runGoogleSearchEnrichment error:", error)
				} else {
					self.statusMessage = "GoogleSearch enrichment complete."
				}
				completion()
			}
		}.resume()
	}

	// Apollo enrichment step
	func runApollo(completion: @escaping () -> Void) {
		// Collect unique company links
		self.statusMessage = "Investigating Jobs..."
		let companyLinks = jobs.compactMap { $0.company_url }.filter { !$0.isEmpty }
		guard let url = URL(string: "http://192.168.1.143:5000/apollo_bulk_enrich") else { completion(); return }
		var request = URLRequest(url: url)
		request.httpMethod = "POST"
		request.timeoutInterval = 600
		request.setValue("application/json", forHTTPHeaderField: "Content-Type")
		let body: [String: Any] = ["company_links": companyLinks]
		request.httpBody = try? JSONSerialization.data(withJSONObject: body)

		URLSession.shared.dataTask(with: request) { data, response, error in
			guard let data = data,
				  let result = try? JSONSerialization.jsonObject(with: data) as? [String: String] else {
				DispatchQueue.main.async {
					self.statusMessage = "Apollo enrichment failed."
					if let error = error { print("runApolloBulkEnrichment error:", error) }
					completion()
				}
				return
			}
			DispatchQueue.main.async {
				for (index, job) in self.jobs.enumerated() {
					if let link = job.company_url, let numEmployees = result[link] {
						self.jobs[index].company_num_employees = numEmployees
					}
				}
				self.statusMessage = "Investigation complete."
				completion()
			}
		}.resume()
	}
}
