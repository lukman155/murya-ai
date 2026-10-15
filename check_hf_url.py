import urllib.request
import re

url = "https://huggingface.co/spaces/theAlpha419/murya-ai"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
res = urllib.request.urlopen(req)
body = res.read().decode("utf-8", errors="ignore")

hf_links = re.findall(r"https://[a-zA-Z0-9\-\.]+\.hf\.space[^\"\'>\s]*", body)
print("HF space links found:", list(set(hf_links)))

# Search for any iframe
iframes = re.findall(r"<iframe[^>]+>", body)
print("Iframes found:")
for iframe in iframes:
    print(" ", iframe)
