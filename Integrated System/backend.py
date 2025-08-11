import os
import csv
from jobspy import scrape_jobs
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/JobSpy", methods=["POST"])
def JobSpy():
    # Parse incoming JSON
    data = request.get_json()
    if not data:
        print("No JSON received")
        return jsonify({"error": "No JSON received"}), 400

    # Extract parameters from JSON
    site_name = data.get("site_name", ["linkedin"])
    search_term = data.get("search_term", "Data Analyst")
    location = data.get("location", "United Kingdom")
    results_wanted = int(data.get("results_wanted", 10) or 10)
    linkedin_fetch_description = data.get("fetch_description", True)
    rotate_proxies = data.get("rotate_proxies", True)
    print("Running")
    
    # Load Proxies List
    with open("JobSpy/Proxies/working_proxies.txt") as f:
        proxy_list = [line.strip() for line in f if line.strip()]
    print("Fetched Proxies List")

    # Extract Jobs
    jobs = scrape_jobs(
        site_name=site_name,
        search_term=search_term,
        location=location,
        results_wanted=results_wanted,
        linkedin_fetch_description=linkedin_fetch_description,
        proxies=proxy_list,
        rotate_proxies=rotate_proxies
    )
    print(f"Found {len(jobs)} jobs")
    print(jobs.head())
    jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)

    # CSV Formatting
    df = pd.read_csv("jobs.csv")
    df.insert(0, "job_number", range(1, len(df) + 1))
    df = df.drop(columns=["id"])
    df.to_csv("jobs_numbered.csv", index=False)
    os.remove("jobs.csv")

    return jsonify({"message": "Job extraction complete!", "count": len(df)})

if __name__ == "__main__":
    app.run(debug=True, host="192.168.1.143", port=5000)
