import requests
from bs4 import beau

# Fetch Website
url = "https://www.ptt.cc/bbs/NBA/index.html"
response = requests.get(url)
if response.status_code == 200:
    # Write website data
    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
else:
    print("Error")