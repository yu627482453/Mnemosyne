import urllib.request
import urllib.parse
import os
from datetime import datetime

images = [
    "https://raw.githubusercontent.com/datawhalechina/Hello-Agents/main/docs/images/1-figures/[银行卡]-0.png",
    "https://raw.githubusercontent.com/datawhalechina/Hello-Agents/main/docs/images/1-figures/[银行卡]-1.png",
    "https://raw.githubusercontent.com/datawhalechina/Hello-Agents/main/docs/images/1-figures/[银行卡]-2.png",
    "https://raw.githubusercontent.com/datawhalechina/Hello-Agents/main/docs/images/1-figures/[银行卡]-3.png",
    "https://raw.githubusercontent.com/datawhalechina/Hello-Agents/main/docs/images/1-figures/[银行卡]-4.png",
    "https://raw.githubusercontent.com/datawhalechina/Hello-Agents/main/docs/images/1-figures/[银行卡]-6.png",
    "https://raw.githubusercontent.com/datawhalechina/Hello-Agents/main/docs/images/1-figures/[银行卡]-5.png",
    "https://raw.githubusercontent.com/datawhalechina/Hello-Agents/main/docs/images/1-figures/[银行卡]-18.png"
]

base_dir = "D:/obsidian/0001-resource/3000-Agent"
os.makedirs(base_dir, exist_ok=True)

downloaded = []
failed = []

for idx, url in enumerate(images, 1):
    try:
        # URL encode the path part
        parts = urllib.parse.urlsplit(url)
        encoded_path = urllib.parse.quote(parts.path.encode('utf-8'))
        encoded_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, encoded_path, '', ''))

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        ext = 'png'
        filename = f"agent-introduction-{timestamp}-{idx}.{ext}"
        filepath = os.path.join(base_dir, filename)

        req = urllib.request.Request(encoded_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())

        downloaded.append(f"0001-resource/3000-Agent/{filename}")
        print(f"OK {idx}/8: {filename}")
    except Exception as e:
        failed.append(url)
        print(f"FAIL {idx}/8: {str(e)[:50]}")

print(f"\nSuccess: {len(downloaded)}, Failed: {len(failed)}")
if downloaded:
    print("Paths:")
    for p in downloaded:
        print(p)
if failed:
    print("\nFailed URLs:")
    for u in failed:
        print(u)
