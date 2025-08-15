from googlesearch import search
from flask import request
import os
import csv
from jobspy import scrape_jobs
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from google import genai
import ssl

app = Flask(__name__)
CORS(app)

ssl._create_default_https_context = ssl._create_unverified_context

@app.route("/JobSpy", methods=["POST"])
def JobSpy():
    try:
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
        keep_cols = [
            "title",
            "company",
            "location",
            "date_posted",
            "company_url"
        ]
        df.insert(0, "job_number", range(1, len(df) + 1))
        df = df[[col for col in ["job_number"] + keep_cols if col in df.columns]]

        df.to_csv("jobs_numbered.csv", index=False)
        os.remove("jobs.csv")
        return jsonify({"message": "Job extraction complete!", "count": len(df)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Apollo bulk enrichment endpoint

@app.route("/apollo_bulk_enrich", methods=["POST"])
def apollo_bulk_enrich():
    # Read company links from jobs_numbered.csv
    df = pd.read_csv("jobs_numbered.csv")
    company_links = df["company_url"].dropna().unique().tolist()

    # Extract domains from company URLs
    domains = []
    for url in company_links:
        match = re.search(r'https?://(?:www\.)?([^/]+)', str(url))
        if match:
            domain = match.group(1)
            domains.append(domain)

    # Call Apollo bulk enrichment API
    apollo_url = f"https://api.apollo.io/api/v1/organizations/bulk_enrich?" + "&".join([f"domains[]={d}" for d in domains])
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "x-api-key": "-Dapnpp9DM6vnZoKUO2WFQ"
    }
    try:
        response = requests.post(apollo_url, headers=headers)
        org_results = {}
        if response.status_code == 200:
            data = response.json()
            for org in data.get("organizations", []):
                domain = org.get("primary_domain", org.get("domain", ""))
                dept_headcount = org.get("departmental_head_count", {})
                total_dept_headcount = sum(dept_headcount.values()) if dept_headcount else None
                org_results[domain] = total_dept_headcount
                print(f"Apollo fetched for domain {domain}:")
                print(f"SUM Department Headcount: {total_dept_headcount}\n")
        else:
            return jsonify({"error": "Apollo API call failed", "status": response.status_code, "response": response.text}), 500

        # Update jobs_numbered.csv with SUM department headcount only
        # Remove 'countEmploy' column if present
        if "countEmploy" in df.columns:
            df = df.drop(columns=["countEmploy"])
        df.to_csv("jobs_numbered.csv", index=False)
        return jsonify(org_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    # New endpoint to enrich jobs_numbered.csv with Google Search
@app.route("/enrich_googlesearch", methods=["POST"])
def enrich_googlesearch():
    df = pd.read_csv("jobs_numbered.csv")
    def get_google_company_url(company_name):
        try:
            for url in search(company_name, num=1, stop=1, pause=2):
                return url
        except Exception as e:
            print(f"GoogleSearch failed for {company_name}: {e}")
            return None
    try:
        for idx, row in df.iterrows():
            company_name = row["company"]
            url = get_google_company_url(company_name)
            if not url:
                print(f"GoogleSearch failed to find URL for {company_name}")
                df.at[idx, "company_url"] = ""
            else:
                df.at[idx, "company_url"] = url
                print(f"GoogleSearch enrichment for company {company_name}:")
                print(f"URL: {url}")
        df.to_csv("jobs_numbered.csv", index=False)
        return jsonify({
            "message": "GoogleSearch enrichment complete!",
            "count": len(df),
        })
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

# New endpoint to serve jobs_numbered.csv as JSON
@app.route("/jobs", methods=["GET"])
def get_jobs():
    try:
        df = pd.read_csv("jobs_numbered.csv")
        # Drop problematic columns before cleaning
        # Only drop 'description', keep 'company_description' for enrichment
        if "description" in df.columns:
            df = df.drop(columns=["description"])
        # Replace NaN/None and string 'None'/'NaN'/empty string with None (which becomes null in JSON)
        df = df.where(pd.notnull(df), None)
        df = df.replace({"None": None, "NaN": None, "": None})
        df = df.reset_index(drop=True)
        jobs = df.to_dict(orient="records")
        return jsonify(jobs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="192.168.1.143", port=5000)

