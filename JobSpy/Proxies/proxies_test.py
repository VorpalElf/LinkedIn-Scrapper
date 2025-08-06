import requests
import time

input_file = "Proxies/proxies_list.txt"
output_file = "Proxies/working_proxies.txt"

with open(input_file) as f:
    proxies = [line.strip() for line in f if line.strip()]

total_proxies = len(proxies)
working = []
success_count = 0
failed_count = 0

max_response_time = 10  # seconds

for idx, proxy in enumerate(proxies, 1):
    try:
        start = time.time()
        resp = requests.get(
            "https://www.linkedin.com",
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            timeout=5
        )
        elapsed = time.time() - start
        if resp.status_code == 200 and elapsed <= max_response_time:
            print(f"{proxy}: OK ({elapsed:.2f}s)")
            working.append(proxy)
            success_count += 1
        else:
            print(f"{proxy}: Status {resp.status_code} ({elapsed:.2f}s)")
            failed_count += 1
    except Exception as e:
        print(f"{proxy}: Failed ({e})")
        failed_count += 1
    print(f"Progress: {idx}/{total_proxies}\n")

with open(output_file, "w") as f:
    for proxy in working:
        f.write(proxy + "\n")

print(f"Working proxies saved to {output_file}")
print(f"Working (fast) proxies saved to {output_file}")
print(f"Successful proxies: {success_count}/{total_proxies}")
print(f"Failed proxies: {failed_count}/{total_proxies}")