# JobHunter Xcode Project

## Overview
JobHunter is a SwiftUI-based iOS/macOS app for searching and enriching job listings. It integrates with a Python backend to fetch, enrich, and display job data.

## Prerequisites
- Xcode 13 or later
- macOS 12 or later
- Python 3.8+
- Backend server running (see below)

## Project Structure
- `JobHunter/JobHunter/` — Main SwiftUI app code
- `JobHunter/JobHunter/JobHunterApp.swift` — App entry point
- `JobHunter/JobHunter/loadViewModel.swift` — ViewModel for job fetching/enrichment
- `JobHunter/JobHunter/JobResultsView.swift` — Job results UI
- `JobHunter/JobHunter/ContentView.swift` — Main content view

## Setup Instructions

### 1. Backend Setup
1. Navigate to the backend directory:
   ```sh
   cd /Users/s20131085/Desktop/CIT/Try Petals/Integrated System
   ```
2. Install Python dependencies:
   ```sh
   pip install flask flask-cors pandas requests googlesearch-python jobspy google-generativeai
   ```
3. Set required environment variables (e.g., Apollo API key):
   ```sh
   export APOLLO_API_KEY="your_apollo_api_key"
   ```
4. Start the backend server:
   ```sh
   python backend2.py
   ```

### 2. Xcode Project Setup
1. Open `JobHunter.xcodeproj` in Xcode.
2. Build and run the project on your simulator or device.
3. Ensure your device/simulator is on the same network as the backend server.

## Usage
- Enter job search parameters in the app UI.
- Tap to fetch jobs. The app will:
  1. Query the backend for jobs.
  2. Run enrichment steps (Gemini, GoogleSearch, Apollo).
  3. Display enriched job results, including company info and employee count.

## Troubleshooting
- If jobs do not appear, check backend logs for errors.
- Ensure backend server is running and accessible at the configured IP address.
- Make sure all required Python packages are installed.
- For API keys, use environment variables (never hardcode in code).

## Customization
- Edit SwiftUI views in `JobHunter/JobHunter/` for UI changes.
- Modify backend enrichment logic in `backend2.py` for data changes.

## License
This project is for educational and research purposes only.
