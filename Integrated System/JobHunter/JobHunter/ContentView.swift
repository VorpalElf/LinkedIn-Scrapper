//
//  ContentView.swift
//  JobHunter
//
//  Created by Jeremy Lo on 14/8/25.
//

import SwiftUI

struct ContentView: View {
    enum Sites: String, CaseIterable, Identifiable {
        case LinkedIn, Indeed, Glassdoor
        var id: Self { self }
    }
    @State private var searchTerm: String = ""
    @State private var location: String = ""
    @State private var numResults: Int = 10
    @State private var hoursAgo: Int = 12
    @State private var linkedinOn: Bool = true
    @State private var indeedOn: Bool = false
    @State private var glassdoorOn: Bool = false
    @State private var fullDescription: Bool = true

    @StateObject private var viewModel = loadViewModel()
    @State private var showResults = false

    var body: some View {
        NavigationView {
            VStack {
                Text("Job Hunter 🕵️‍♂️")
                    .font(.title)
                    .fontWeight(.bold)
                    .padding()

                HStack {
                    Image(systemName: "magnifyingglass")
                        .scaleEffect(1.25)
                    TextField("Job Title", text: $searchTerm)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                        .frame(width: 300)
                }
                .padding()

                HStack {
                    Image(systemName: "mappin.and.ellipse")
                        .scaleEffect(1.25)
                    TextField("Location", text: $location)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                        .frame(width: 300)
                }
                .padding()

                HStack {
                    Image(systemName: "number")
                        .scaleEffect(1.25)
                    TextField("No. of Results", value: $numResults, format: .number)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                        .frame(width: 150)
                        .keyboardType(.numberPad)
                    Spacer()
                    Image(systemName: "clock")
                        .scaleEffect(1.25)
                    TextField("Hours Ago", value: $hoursAgo, format: .number)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                        .frame(width: 150)
                        .keyboardType(.numberPad)
                }
                .padding()

                VStack(alignment: .leading, spacing: 8) {
                    Text("Sites Sources")
                        .font(.headline)
                    Toggle(isOn: $linkedinOn) {
                        Text("LinkedIn")
                    }
                    Toggle(isOn: $indeedOn) {
                        Text("Indeed")
                    }
                    Toggle(isOn: $glassdoorOn) {
                        Text("Glassdoor")
                    }
                }

                if viewModel.isLoading {
                    ProgressView("Loading...")
                        .padding()
                }
                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .padding()
                }

                Button {
                    let selectedSites: [String] = [
                        linkedinOn ? "linkedin" : nil,
                        indeedOn ? "indeed" : nil,
                        glassdoorOn ? "glassdoor" : nil
                    ].compactMap { $0 }
                    viewModel.fetchJobs(
                        searchTerm: searchTerm,
                        location: location,
                        numResults: numResults,
                        sitesPicked: selectedSites,
                        fullDescription: fullDescription
                    ) { success in
                        if success {
                            showResults = true
                        }
                    }
                } label: {
                    Text("Search")
                        .padding()
                        .padding(.horizontal, 13)
                        .background(Color(.green))
                        .foregroundColor(.white)
                        .font(.title2)
                        .fontWeight(.bold)
                        .cornerRadius(8)
                        .frame(width: 180)
                }

                NavigationLink(
                    destination: JobResultsView(jobs: viewModel.jobs),
                    isActive: $showResults
                ) {
                    EmptyView()
                }
            }
            .padding()
            .onTapGesture {
                hideKeyboard()
            }
        }
    }
}


// Helper to hide keyboard
extension View {
    func hideKeyboard() {
        UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
    }
}

#Preview {
    ContentView()
}
